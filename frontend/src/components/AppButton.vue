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
  width: 100%;
  border: 0;
  border-radius: 10px;
  padding: 0.85rem 1.2rem;
  color: #fff;
  font-weight: 700;
  background: linear-gradient(135deg, var(--brand-start), var(--brand-end));
  box-shadow: 0 8px 18px rgba(0, 109, 119, 0.22);
}

button:hover:not(:disabled) {
  filter: brightness(1.03);
}

button:disabled {
  opacity: 0.6;
}
</style>
