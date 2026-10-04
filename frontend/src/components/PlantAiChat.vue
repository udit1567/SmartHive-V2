<script setup>
import { computed, onMounted, ref, watch } from "vue";

import { request } from "@/api/client";
import MarkdownText from "@/components/MarkdownText.vue";
import { useAiChatStore } from "@/stores/aiChat";
import { useAuthStore } from "@/stores/auth";

const props = defineProps({
  refreshSignal: { type: Number, default: 0 },
});

const auth = useAuthStore();
const ai = useAiChatStore();

const history = ref([]);
const brokenImageUrls = ref(new Set());
const galleryError = ref("");
const selectedImageUrl = ref("");
const selectedImage = ref(null);
const imageError = ref("");
const imageLoading = ref(false);

const messages = ref([]);
const draft = ref("");
const busy = ref(false);
const error = ref("");

const threads = ref([]);
const threadsError = ref("");
const activeThreadId = ref(null);

async function loadThreads() {
  threadsError.value = "";
  try {
    const data = await request("/chat/threads", { token: auth.token });
    threads.value = data.threads ?? [];
  } catch (err) {
    threadsError.value = err.message;
  }
}

async function selectThread(id) {
  if (busy.value || id === activeThreadId.value) {
    return;
  }
  error.value = "";
  try {
    const data = await request(`/chat/threads/${id}`, { token: auth.token });
    activeThreadId.value = id;
    messages.value = (data.messages ?? []).map((m) => ({
      role: m.role,
      content: m.content,
      imageUrl: m.imageUrl || "",
    }));
  } catch (err) {
    error.value = err.message;
  }
}

function startNewChat() {
  if (busy.value) {
    return;
  }
  activeThreadId.value = null;
  messages.value = [];
  error.value = "";
}

async function deleteThread(id) {
  try {
    await request(`/chat/threads/${id}`, { method: "DELETE", token: auth.token });
    threads.value = threads.value.filter((t) => t.id !== id);
    if (activeThreadId.value === id) {
      startNewChat();
    }
  } catch (err) {
    threadsError.value = err.message;
  }
}

async function ensureThread() {
  if (activeThreadId.value) {
    return activeThreadId.value;
  }
  const thread = await request("/chat/threads", { method: "POST", token: auth.token, json: {} });
  threads.value.unshift(thread);
  activeThreadId.value = thread.id;
  return thread.id;
}

function persistMessage(threadId, message) {
  return request(`/chat/threads/${threadId}/messages`, {
    method: "POST",
    token: auth.token,
    json: {
      role: message.role,
      content: message.content,
      imageUrl: message.imageUrl || null,
    },
  });
}

async function loadHistory() {
  galleryError.value = "";
  try {
    const data = await request("/plant_detections", { deviceToken: auth.deviceToken });
    history.value = data.plant_detections ?? [];
    brokenImageUrls.value = new Set();
  } catch (err) {
    galleryError.value = err.message;
  }
}

watch(() => props.refreshSignal, loadHistory);

const availableHistory = computed(() => {
  const seenUrls = new Set();
  const deduped = [];
  for (const entry of history.value) {
    if (brokenImageUrls.value.has(entry.imageUrl) || seenUrls.has(entry.imageUrl)) {
      continue;
    }
    seenUrls.add(entry.imageUrl);
    deduped.push(entry);
  }
  return deduped;
});

function markImageBroken(url) {
  brokenImageUrls.value = new Set(brokenImageUrls.value).add(url);
}

function topLabel(entry) {
  if (!entry.classes?.length) {
    return "No disease detected";
  }
  const top = [...entry.classes].sort((a, b) => b.confidence - a.confidence)[0];
  return `${top.class} (${Math.round(top.confidence * 100)}%)`;
}

function describeEntry(entry) {
  if (!entry?.classes?.length) {
    return "This scan found no disease.";
  }
  const lines = entry.classes.map((item) => `${item.class} (${Math.round(item.confidence * 100)}% confidence)`);
  return `This scan detected: ${lines.join(", ")}.`;
}

async function urlToBase64(url) {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Could not load that image (${response.status})`);
  }
  const blob = await response.blob();
  const mimeType = blob.type || "image/jpeg";
  const base64 = await new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result).split(",")[1] ?? "");
    reader.onerror = () => reject(new Error("Could not read that image."));
    reader.readAsDataURL(blob);
  });
  return { mimeType, base64 };
}

async function selectImage(url) {
  imageError.value = "";
  if (selectedImageUrl.value === url) {
    selectedImageUrl.value = "";
    selectedImage.value = null;
    return;
  }
  selectedImageUrl.value = url;
  imageLoading.value = true;
  try {
    selectedImage.value = await urlToBase64(url);
  } catch (err) {
    imageError.value = err.message;
    selectedImageUrl.value = "";
    selectedImage.value = null;
  } finally {
    imageLoading.value = false;
  }
}

function clearImageSelection() {
  selectedImageUrl.value = "";
  selectedImage.value = null;
  imageError.value = "";
}

async function sendMessage(text) {
  const content = text.trim();
  if (!content || busy.value) {
    return;
  }
  error.value = "";
  const userMessage = { role: "user", content, image: selectedImage.value ?? undefined };
  const imageUrlForBubble = selectedImageUrl.value;
  messages.value.push({ ...userMessage, imageUrl: imageUrlForBubble });
  const assistantIndex = messages.value.push({ role: "assistant", content: "" }) - 1;
  clearImageSelection();
  busy.value = true;
  try {
    const threadId = await ensureThread();
    await persistMessage(threadId, { role: "user", content, imageUrl: imageUrlForBubble });
    await ai.streamChat([...messages.value.slice(0, -1).map(({ imageUrl, ...rest }) => rest)], (_, full) => {
      // Mutate through the reactive array (not a plain captured reference) so
      // each streamed chunk actually triggers a re-render instead of only
      // showing the final text once busy.value flips back at the end.
      messages.value[assistantIndex].content = full;
    });
    await persistMessage(threadId, { role: "assistant", content: messages.value[assistantIndex].content });
    await loadThreads();
  } catch (err) {
    error.value = err.message;
    messages.value.splice(assistantIndex, 1);
  } finally {
    busy.value = false;
  }
}

async function onSubmit() {
  const text = draft.value;
  draft.value = "";
  await sendMessage(text);
}

async function discussSelectedImage() {
  if (!selectedImage.value) {
    return;
  }
  const entry = history.value.find((item) => item.imageUrl === selectedImageUrl.value);
  await sendMessage(
    `${describeEntry(entry)} What can you tell me about this plant image? Point out any visible disease or stress and suggest what to do next.`
  );
}

onMounted(() => {
  ai.load();
  loadHistory();
  loadThreads();
});
</script>

<template>
  <section class="chat">
    <header>
      <h2>Ask the plant AI</h2>
      <p>Bring your own Gemini API key or a local Ollama model to discuss detections.</p>
    </header>

    <div class="layout">
      <aside class="threads">
        <button type="button" class="new-thread" :disabled="busy" @click="startNewChat">+ New chat</button>
        <p v-if="threadsError" class="err">{{ threadsError }}</p>
        <p v-else-if="!threads.length" class="hint">No saved conversations yet.</p>
        <ul v-else class="thread-list">
          <li v-for="t in threads" :key="t.id">
            <button
              type="button"
              class="thread-item"
              :class="{ on: t.id === activeThreadId }"
              :title="t.title"
              @click="selectThread(t.id)"
            >
              <span class="thread-title">{{ t.title }}</span>
              <span class="thread-date">{{ t.updatedAt }}</span>
            </button>
            <button
              type="button"
              class="thread-delete"
              title="Delete conversation"
              @click="deleteThread(t.id)"
            >
              ×
            </button>
          </li>
        </ul>
      </aside>

      <div class="conversation">
        <p class="provider-hint">
          Using {{ ai.settings.provider === "gemini" ? "Gemini" : "Ollama" }}
          (<code>{{ ai.settings.provider === "gemini" ? ai.settings.geminiModel : ai.settings.ollamaModel }}</code>).
          Change provider or model in <router-link to="/app/account">Settings</router-link>.
        </p>

        <div class="picker">
          <h3>Talk about a detected image</h3>
          <p v-if="galleryError" class="err">{{ galleryError }}</p>
          <p v-else-if="!availableHistory.length" class="hint">
            No saved detections yet. Run a scan above, or just ask a question below.
          </p>
          <div v-else class="thumbs">
            <button
              v-for="entry in availableHistory"
              :key="entry.id"
              type="button"
              class="thumb"
              :class="{ on: selectedImageUrl === entry.imageUrl }"
              :title="`${entry.timestamp} — ${topLabel(entry)}`"
              @click="selectImage(entry.imageUrl)"
            >
              <img :src="entry.imageUrl" alt="Saved detection" @error="markImageBroken(entry.imageUrl)" />
              <span class="caption">{{ topLabel(entry) }}</span>
            </button>
          </div>

          <div v-if="selectedImageUrl" class="selected-bar">
            <span v-if="imageLoading">Loading image…</span>
            <span v-else>Image selected — it'll be sent with your next message.</span>
            <button type="button" @click="clearImageSelection">Clear</button>
            <button type="button" class="discuss" :disabled="busy || imageLoading" @click="discussSelectedImage">
              Discuss this image
            </button>
          </div>
          <p v-if="imageError" class="err">{{ imageError }}</p>
        </div>

        <div class="log">
          <p v-if="!messages.length" class="empty">
            Pick a detected image above, or just write down whatever you want to ask.
          </p>
          <div v-for="(message, index) in messages" :key="index" :class="['bubble', message.role]">
            <img v-if="message.imageUrl" :src="message.imageUrl" alt="Attached detection" class="attached" />
            <MarkdownText v-if="message.content" :text="message.content" />
            <span v-else class="typing">Thinking…</span>
          </div>
        </div>

        <p v-if="error" class="err">{{ error }}</p>

        <form class="composer" @submit.prevent="onSubmit">
          <input v-model="draft" type="text" placeholder="Ask about this plant…" :disabled="busy" />
          <button type="submit" :disabled="busy || !draft.trim()">Send</button>
        </form>
      </div>
    </div>
  </section>
</template>

<style scoped>
.chat {
  background: #fff;
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 1.2rem 1.25rem 1.3rem;
  margin-bottom: 1.25rem;
}

header p {
  color: var(--muted);
  margin-top: 0.3rem;
}

h2 {
  font-size: 1.2rem;
}

.layout {
  display: flex;
  gap: 1.1rem;
  align-items: flex-start;
  margin-top: 1rem;
}

.threads {
  flex: 0 0 13rem;
  display: grid;
  gap: 0.6rem;
  align-content: start;
}

.new-thread {
  border: 1px dashed var(--oasis-water);
  background: var(--oasis-mist);
  color: var(--brand);
  border-radius: 8px;
  padding: 0.55rem 0.7rem;
  font-weight: 800;
  font-size: 0.85rem;
}

.new-thread:disabled {
  opacity: 0.6;
}

.thread-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 0.35rem;
  max-height: 22rem;
  overflow-y: auto;
}

.thread-list li {
  display: flex;
  align-items: stretch;
  gap: 0.3rem;
  border-top: 0;
  padding: 0;
}

.thread-item {
  flex: 1;
  min-width: 0;
  text-align: left;
  border: 1px solid transparent;
  border-radius: 8px;
  padding: 0.5rem 0.6rem;
  display: grid;
  gap: 0.15rem;
  background: var(--oasis-mist);
}

.thread-item.on {
  border-color: var(--oasis-teal);
  background: #fff;
}

.thread-title {
  font-weight: 700;
  font-size: 0.82rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.thread-date {
  font-size: 0.68rem;
  color: var(--muted);
}

.thread-delete {
  flex: none;
  border: 0;
  background: transparent;
  color: var(--muted);
  font-size: 1rem;
  padding: 0 0.3rem;
}

.thread-delete:hover {
  color: var(--danger);
}

.conversation {
  flex: 1;
  min-width: 0;
}

@media (max-width: 840px) {
  .layout {
    flex-direction: column;
  }

  .threads {
    flex-basis: auto;
    width: 100%;
  }

  .thread-list {
    max-height: 12rem;
  }
}

.provider-hint {
  color: var(--muted);
  font-size: 0.78rem;
  margin-bottom: 0.9rem;
}

.provider-hint code {
  background: var(--oasis-mist);
  border-radius: 4px;
  padding: 0.1rem 0.3rem;
}

.provider-hint a {
  color: var(--brand);
  font-weight: 700;
}

.hint {
  color: var(--muted);
  font-size: 0.78rem;
}

.hint code {
  background: var(--oasis-mist);
  border-radius: 4px;
  padding: 0.1rem 0.3rem;
}

.picker {
  margin-top: 1.1rem;
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 0.9rem;
}

.picker h3 {
  font-size: 0.95rem;
  margin-bottom: 0.5rem;
}

.thumbs {
  display: flex;
  gap: 0.55rem;
  overflow-x: auto;
  padding-bottom: 0.3rem;
}

.thumb {
  flex: none;
  width: 5.4rem;
  border-radius: 8px;
  border: 2px solid transparent;
  padding: 0;
  overflow: hidden;
  background: var(--oasis-mist);
  display: grid;
  gap: 0.2rem;
}

.thumb.on {
  border-color: var(--oasis-teal);
}

.thumb img {
  width: 100%;
  height: 4.2rem;
  object-fit: cover;
  display: block;
}

.thumb .caption {
  font-size: 0.62rem;
  font-weight: 700;
  color: var(--muted);
  padding: 0 0.3rem 0.3rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.selected-bar {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-top: 0.7rem;
  font-size: 0.82rem;
  color: var(--muted);
  flex-wrap: wrap;
}

.selected-bar button {
  border: 0;
  border-radius: 8px;
  padding: 0.45rem 0.8rem;
  font-weight: 700;
  font-size: 0.8rem;
  background: var(--oasis-mist);
  color: var(--muted);
}

.selected-bar .discuss {
  background: var(--oasis-teal);
  color: #fff;
}

.log {
  margin-top: 1.1rem;
  display: grid;
  gap: 0.55rem;
  min-height: 3rem;
}

.empty {
  color: var(--muted);
  font-size: 0.85rem;
}

.bubble {
  border-radius: 10px;
  padding: 0.6rem 0.8rem;
  font-size: 0.9rem;
  max-width: 85%;
}

.bubble.user {
  background: var(--oasis-teal);
  color: #fff;
  justify-self: end;
}

.bubble.assistant {
  background: var(--oasis-mist);
  color: var(--ink);
  justify-self: start;
}

.bubble .attached {
  display: block;
  max-width: 100%;
  max-height: 10rem;
  border-radius: 8px;
  margin-bottom: 0.4rem;
  object-fit: cover;
}

.bubble .typing {
  opacity: 0.75;
}

.err {
  color: var(--danger);
  background: #fef2f2;
  border-radius: 8px;
  padding: 0.6rem 0.75rem;
  margin-top: 0.7rem;
  font-size: 0.85rem;
}

.composer {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
}

.composer input {
  flex: 1;
  min-width: 0;
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 0.65rem 0.75rem;
}

.composer button {
  border: 0;
  border-radius: 8px;
  padding: 0.65rem 1rem;
  font-weight: 800;
  color: #fff;
  background: var(--oasis-teal);
}

.composer button:disabled {
  opacity: 0.6;
}
</style>
