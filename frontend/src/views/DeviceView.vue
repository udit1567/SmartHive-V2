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
    <p class="eyebrow">Hardware</p>
    <h1>The quiet key.</h1>
    <p class="lede">
      Send this token as the Authorization header from your board. It is not a
      password. Treat it as a household spare.
    </p>
    <button type="button" class="token" @click="copy">
      {{ auth.deviceToken || "—" }}
    </button>
    <p class="hint">{{ copied ? "Copied." : "Click to copy." }}</p>
  </section>
</template>

<style scoped>
.eyebrow {
  letter-spacing: 0.18em;
  text-transform: uppercase;
  font-size: 0.7rem;
  color: var(--muted);
}

h1 {
  font-size: clamp(2.6rem, 5vw, 4.2rem);
  margin: 0.4rem 0 1rem;
}

.lede {
  max-width: 32rem;
  color: var(--muted);
}

.token {
  display: block;
  margin-top: 2.5rem;
  background: none;
  border: 0;
  border-bottom: 1px solid var(--line);
  padding: 0.8rem 0;
  font-family: var(--serif);
  font-size: 2rem;
  letter-spacing: 0.08em;
}

.hint {
  margin-top: 0.7rem;
  color: var(--muted);
  font-size: 0.85rem;
}
</style>
