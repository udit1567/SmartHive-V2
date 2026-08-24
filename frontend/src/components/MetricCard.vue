<script setup>
defineProps({
  label: { type: String, required: true },
  value: { type: [String, Number], default: "—" },
  unit: { type: String, default: "" },
});
</script>

<template>
  <article>
    <p class="kicker">{{ label }}</p>
    <p class="figure">
      {{ value ?? "—" }}
      <span v-if="unit && value !== null && value !== undefined && value !== '—'">{{ unit }}</span>
    </p>
  </article>
</template>

<style scoped>
article {
  padding: 1.25rem 0;
  border-top: 1px solid var(--line);
}

.kicker {
  font-size: 0.7rem;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--muted);
}

.figure {
  font-family: var(--serif);
  font-size: 2.6rem;
  margin-top: 0.35rem;
}

span {
  font-size: 1rem;
  color: var(--muted);
  margin-left: 0.2rem;
}
</style>
