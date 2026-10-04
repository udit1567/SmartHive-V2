import { defineStore } from "pinia";
import { reactive, watch } from "vue";

import { useAuthStore } from "@/stores/auth";

function storageKey(uid) {
  return `smarthive.ai.${uid}`;
}

function defaults() {
  return {
    provider: "gemini",
    geminiApiKey: "",
    geminiModel: "gemini-2.5-flash",
    ollamaBaseUrl: "http://localhost:11434",
    ollamaModel: "llama3",
  };
}

const SYSTEM_PROMPT =
  "You are the SmartHive Plant AI, a plant health consultant embedded in a hive and crop " +
  "monitoring dashboard. Advise the grower strictly in terms of plant disease, pests, and " +
  "general plant/leaf health: interpret leaf-disease detections (class name and confidence), " +
  "read attached leaf photos for visible symptoms, and give practical diagnosis, treatment, " +
  "and prevention guidance. If a question is unrelated to plant health, briefly redirect the " +
  "conversation back to plant disease consultation. Keep answers concise and actionable.";

async function readSseStream(response, onDelta) {
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let full = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) {
      break;
    }
    buffer += decoder.decode(value, { stream: true });
    const events = buffer.split("\n\n");
    buffer = events.pop() ?? "";
    for (const event of events) {
      const line = event.split("\n").find((entry) => entry.startsWith("data:"));
      if (!line) {
        continue;
      }
      const jsonStr = line.slice(5).trim();
      if (!jsonStr || jsonStr === "[DONE]") {
        continue;
      }
      try {
        const parsed = JSON.parse(jsonStr);
        const text = parsed?.candidates?.[0]?.content?.parts?.map((part) => part.text).join("") ?? "";
        if (text) {
          full += text;
          onDelta(text, full);
        }
      } catch {
        // ignore partial/malformed SSE frame
      }
    }
  }
  return full;
}

async function readNdjsonStream(response, onDelta) {
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let full = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) {
      break;
    }
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";
    for (const line of lines) {
      if (!line.trim()) {
        continue;
      }
      try {
        const parsed = JSON.parse(line);
        const text = parsed?.message?.content ?? "";
        if (text) {
          full += text;
          onDelta(text, full);
        }
      } catch {
        // ignore partial/malformed line
      }
    }
  }
  return full;
}

export const useAiChatStore = defineStore("aiChat", () => {
  const settings = reactive(defaults());

  // The Gemini API key lives in the backend (User.gemini_api_key) so it
  // follows the account across devices — everything else here (provider
  // choice, model names, Ollama URL) is a local-device preference and stays
  // in localStorage.
  async function load(profile) {
    const auth = useAuthStore();
    Object.assign(settings, defaults());
    if (!auth.uid) {
      return;
    }
    try {
      const raw = localStorage.getItem(storageKey(auth.uid));
      if (raw) {
        const stored = JSON.parse(raw);
        delete stored.geminiApiKey;
        Object.assign(settings, stored);
      }
    } catch {
      // keep defaults
    }
    try {
      const resolvedProfile = profile ?? (await auth.loadProfile());
      settings.geminiApiKey = resolvedProfile?.geminiApiKey ?? "";
    } catch {
      // leave geminiApiKey blank if the profile fetch fails
    }
  }

  function save() {
    const auth = useAuthStore();
    if (!auth.uid) {
      return;
    }
    const { geminiApiKey, ...rest } = settings;
    localStorage.setItem(storageKey(auth.uid), JSON.stringify(rest));
  }

  watch(settings, save, { deep: true });

  const isConfigured = () =>
    settings.provider === "gemini" ? Boolean(settings.geminiApiKey) : Boolean(settings.ollamaBaseUrl);

  async function streamChat(history, onDelta) {
    if (settings.provider === "gemini") {
      return streamGeminiChat(history, onDelta);
    }
    return streamOllamaChat(history, onDelta);
  }

  async function streamGeminiChat(history, onDelta) {
    if (!settings.geminiApiKey) {
      throw new Error("Add your Gemini API key first.");
    }
    const url = `https://generativelanguage.googleapis.com/v1beta/models/${settings.geminiModel}:streamGenerateContent?alt=sse&key=${settings.geminiApiKey}`;
    const contents = history.map((message) => ({
      role: message.role === "assistant" ? "model" : "user",
      parts: [
        ...(message.image
          ? [{ inlineData: { mimeType: message.image.mimeType, data: message.image.base64 } }]
          : []),
        { text: message.content },
      ],
    }));

    const response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        systemInstruction: { parts: [{ text: SYSTEM_PROMPT }] },
        contents,
      }),
    });
    if (!response.ok) {
      const payload = await response.json().catch(() => null);
      throw new Error(payload?.error?.message || `Gemini request failed (${response.status})`);
    }
    const text = await readSseStream(response, onDelta);
    if (!text) {
      throw new Error("Gemini returned an empty response.");
    }
    return text;
  }

  async function streamOllamaChat(history, onDelta) {
    const base = settings.ollamaBaseUrl.replace(/\/+$/, "");
    const response = await fetch(`${base}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        model: settings.ollamaModel,
        stream: true,
        messages: [
          { role: "system", content: SYSTEM_PROMPT },
          ...history.map((message) => ({
            role: message.role,
            content: message.content,
            ...(message.image ? { images: [message.image.base64] } : {}),
          })),
        ],
      }),
    });
    if (!response.ok) {
      throw new Error(`Ollama request failed (${response.status})`);
    }
    const text = await readNdjsonStream(response, onDelta);
    if (!text) {
      throw new Error("Ollama returned an empty response.");
    }
    return text;
  }

  return { settings, load, isConfigured, streamChat };
});
