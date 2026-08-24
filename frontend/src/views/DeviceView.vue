<script setup>
import { ref } from "vue";

import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();
const copied = ref(false);

async function copy() {
  await navigator.clipboard.writeText(auth.deviceToken);
  copied.value = true;
  setTimeout(() => {
    copied.value = false;
  }, 1200);
}
</script>

<template>
  <section>
    <header>
      <h1>Add Device</h1>
      <p>Use this token in the Authorization header from your board.</p>
    </header>
    <article>
      <p class="label">Device token</p>
      <button type="button" @click="copy">{{ auth.deviceToken || "—" }}</button>
      <p class="hint">{{ copied ? "Copied to clipboard." : "Click the token to copy." }}</p>
    </article>
    <article>
      <p class="label">Datastreams</p>
      <p class="hint">
        D1–D8 are unlabeled pins. Send temperature on D1, humidity on D2, or
        anything you map in the dashboard.
      </p>
      <pre>POST /update
Authorization: {{ auth.deviceToken || "YOUR_TOKEN" }}

{ "D1": 24.5, "D2": 61 }</pre>
    </article>
  </section>
</template>

<style scoped>
header {
  margin-bottom: 1.2rem;
}

h1 {
  font-size: 1.8rem;
  font-weight: 800;
}

header p,
.hint {
  color: var(--muted);
}

article {
  background: #fff;
  border-radius: var(--radius);
  padding: 1.3rem;
  box-shadow: var(--shadow);
  max-width: 36rem;
}

.label {
  font-weight: 700;
  margin-bottom: 0.6rem;
}

button {
  display: block;
  width: 100%;
  text-align: left;
  background: var(--oasis-mist);
  border: 1px solid var(--oasis-water);
  border-radius: 10px;
  padding: 0.9rem 1rem;
  font-weight: 800;
  letter-spacing: 0.04em;
  color: var(--brand);
}

.hint {
  margin-top: 0.7rem;
  font-size: 0.9rem;
}

pre {
  margin-top: 0.8rem;
  background: var(--oasis-mist);
  border-radius: 10px;
  padding: 0.9rem 1rem;
  overflow: auto;
  font-size: 0.82rem;
}
</style>
