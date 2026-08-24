<script setup>
defineProps({
  label: { type: String, default: "Continue" },
  busy: { type: Boolean, default: false },
});
</script>

<template>
  <button type="submit" :disabled="busy">
    {{ busy ? "Please wait" : label }}
  </button>
</template>

<style scoped>
button {
  background: var(--ink);
  color: var(--paper);
  border: 0;
  padding: 0.85rem 1.4rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  font-size: 0.72rem;
}

button:disabled {
  opacity: 0.55;
}
</style>
