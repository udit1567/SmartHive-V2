<script setup>
import { computed, onMounted, ref } from "vue";

import { request } from "@/api/client";
import { useAuthStore } from "@/stores/auth";

// Classes worth surfacing first in the picker — security-relevant objects.
const PRIORITY_CLASSES = ["cell phone", "car", "bus", "person", "umbrella", "gun"];

const auth = useAuthStore();
const availableClasses = ref([]);
const selected = ref(new Set());
const telegramConfigured = ref(false);
const loading = ref(true);
const saving = ref(false);
const error = ref("");
const notice = ref("");

const orderedClasses = computed(() => {
  const priority = PRIORITY_CLASSES.filter((name) => availableClasses.value.includes(name));
  const rest = availableClasses.value.filter((name) => !PRIORITY_CLASSES.includes(name)).sort();
  return [...priority, ...rest];
});

const sortedSelected = computed(() => Array.from(selected.value).sort());

const summaryLabel = computed(() =>
  selected.value.size ? `${selected.value.size} class${selected.value.size === 1 ? "" : "es"} selected` : "Select classes"
);

async function load() {
  loading.value = true;
  error.value = "";
  try {
    const [classes, profile] = await Promise.all([
      request("/object_classes"),
      auth.loadProfile(),
    ]);
    availableClasses.value = classes.classes ?? [];
    selected.value = new Set(profile?.watchedClasses ?? []);
    telegramConfigured.value = Boolean(profile?.telegramBotToken && profile?.telegramChatId);
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
}

function toggle(name) {
  const next = new Set(selected.value);
  if (next.has(name)) {
    next.delete(name);
  } else {
    next.add(name);
  }
  selected.value = next;
}

async function save() {
  saving.value = true;
  error.value = "";
  notice.value = "";
  try {
    await auth.updateProfile({ watchedClasses: sortedSelected.value });
    notice.value = "Alert classes saved.";
  } catch (err) {
    error.value = err.message;
  } finally {
    saving.value = false;
  }
}

onMounted(load);
</script>

<template>
  <section class="watch">
    <header>
      <h2>AI Surveillance</h2>
      <p>Watch the live feed for chosen objects and get a Telegram alert the moment one appears.</p>
    </header>

    <p v-if="!loading && !telegramConfigured" class="warn">
      No Telegram bot configured yet. Add a bot token and chat id on the
      <router-link to="/app/account">Settings</router-link> page first.
    </p>

    <p v-if="loading">Loading classes…</p>

    <details v-else class="dropdown">
      <summary>{{ summaryLabel }}</summary>
      <div class="menu">
        <label v-for="name in orderedClasses" :key="name" class="option">
          <input type="checkbox" :checked="selected.has(name)" @change="toggle(name)" />
          {{ name }}
        </label>
      </div>
    </details>

    <p v-if="error" class="err">{{ error }}</p>
    <p v-if="notice" class="ok">{{ notice }}</p>

    <div class="actions">
      <span>{{ selected.size }} selected</span>
      <button type="button" class="save" :disabled="saving || loading" @click="save">
        {{ saving ? "Saving…" : "Save alert classes" }}
      </button>
    </div>
  </section>
</template>

<style scoped>
.watch {
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

.warn {
  background: #fff7ed;
  color: #9a5b13;
  border-radius: 8px;
  padding: 0.7rem 0.8rem;
  margin-top: 0.9rem;
  font-size: 0.85rem;
}

.warn a {
  color: var(--brand);
  font-weight: 700;
}

.dropdown {
  margin-top: 1rem;
  max-width: 22rem;
}

.dropdown summary {
  border: 1px solid var(--line);
  background: var(--oasis-mist);
  border-radius: 8px;
  padding: 0.65rem 0.85rem;
  font-weight: 700;
  color: var(--brand);
  cursor: pointer;
  list-style: none;
}

.dropdown summary::-webkit-details-marker {
  display: none;
}

.dropdown summary::after {
  content: "▾";
  float: right;
}

.menu {
  border: 1px solid var(--line);
  border-top: 0;
  border-radius: 0 0 8px 8px;
  max-height: 16rem;
  overflow-y: auto;
  padding: 0.4rem;
}

.option {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  padding: 0.45rem 0.5rem;
  border-radius: 6px;
  font-weight: 600;
  font-size: 0.9rem;
}

.option:hover {
  background: var(--oasis-mist);
}

.actions {
  display: flex;
  align-items: center;
  gap: 0.9rem;
  margin-top: 1.1rem;
}

.actions span {
  color: var(--muted);
  font-weight: 700;
  font-size: 0.85rem;
}

.save {
  border: 0;
  border-radius: 8px;
  padding: 0.65rem 1rem;
  font-weight: 800;
  color: #fff;
  background: var(--oasis-teal);
}

.save:disabled {
  opacity: 0.6;
}

.err,
.ok {
  border-radius: 8px;
  padding: 0.6rem 0.75rem;
  margin-top: 0.9rem;
  font-size: 0.85rem;
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
