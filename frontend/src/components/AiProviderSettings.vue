<script setup>
import { onMounted, ref } from "vue";

import AppButton from "@/components/AppButton.vue";
import AppField from "@/components/AppField.vue";
import { useAiChatStore } from "@/stores/aiChat";
import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();
const ai = useAiChatStore();

const loading = ref(true);
const error = ref("");
const notice = ref("");
const busy = ref(false);

onMounted(async () => {
  try {
    await ai.load();
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
});

async function onSubmit() {
  error.value = "";
  notice.value = "";
  busy.value = true;
  try {
    const profile = await auth.updateProfile({ geminiApiKey: ai.settings.geminiApiKey });
    ai.settings.geminiApiKey = profile?.geminiApiKey ?? "";
    notice.value = "AI settings saved.";
  } catch (err) {
    error.value = err.message;
  } finally {
    busy.value = false;
  }
}
</script>

<template>
  <article class="ai-provider">
    <header>
      <h2>Plant AI chat</h2>
      <p>Choose which model answers questions about your leaf-disease detections.</p>
    </header>

    <p v-if="loading" class="hint">Loading…</p>
    <form v-else @submit.prevent="onSubmit">
      <label class="provider-select">
        Provider
        <select v-model="ai.settings.provider">
          <option value="gemini">Gemini (Google AI Studio API key)</option>
          <option value="ollama">Ollama (local, open-source)</option>
        </select>
      </label>

      <template v-if="ai.settings.provider === 'gemini'">
        <AppField v-model="ai.settings.geminiApiKey" label="Gemini API key" type="password" autocomplete="off" />
        <AppField v-model="ai.settings.geminiModel" label="Model" autocomplete="off" />
        <p class="hint">Saved with your account — click "Save AI settings" below to store it.</p>
      </template>
      <template v-else>
        <AppField v-model="ai.settings.ollamaBaseUrl" label="Ollama base URL" autocomplete="off" />
        <AppField v-model="ai.settings.ollamaModel" label="Model" autocomplete="off" />
        <p class="hint">
          Run Ollama locally and start it with <code>OLLAMA_ORIGINS=*</code> so the browser is
          allowed to call it from this app. Use a vision-capable model (e.g. <code>llava</code>)
          to discuss images. These fields stay on this device only.
        </p>
      </template>

      <p v-if="error" class="err">{{ error }}</p>
      <p v-if="notice" class="ok">{{ notice }}</p>
      <AppButton label="Save AI settings" :busy="busy" />
    </form>
  </article>
</template>

<style scoped>
.ai-provider {
  background: #fff;
  border-radius: var(--radius);
  padding: 1.25rem 1.3rem 1.3rem;
  box-shadow: var(--shadow);
  flex: 1 1 22rem;
  min-width: 0;
}

header {
  margin-bottom: 0.9rem;
}

h2 {
  font-size: 1.15rem;
}

header p {
  color: var(--muted);
  font-size: 0.85rem;
  margin-top: 0.3rem;
}

form {
  display: grid;
  gap: 0.9rem;
}

.provider-select {
  display: grid;
  gap: 0.4rem;
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--ink);
}

.provider-select select {
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 0.75rem 0.85rem;
  font-weight: 600;
  background: #fff;
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

.err,
.ok {
  border-radius: 8px;
  padding: 0.7rem 0.8rem;
}

.err {
  color: var(--danger);
  background: #fef2f2;
}

.ok {
  color: var(--ok);
  background: #e7f4f4;
}
</style>
