<script setup>
defineProps({
  label: { type: String, required: true },
  value: { type: [String, Number], default: "—" },
  unit: { type: String, default: "" },
  accent: { type: String, default: "linear-gradient(135deg, #006d77, #83c5be)" },
});
</script>

<template>
  <article :style="{ background: accent }">
    <p class="kicker">{{ label }}</p>
    <p class="figure">
      {{ value ?? "—" }}
      <span v-if="unit && value !== '—'">{{ unit }}</span>
    </p>
  </article>
</template>

<style scoped>
article {
  color: #fff;
  border-radius: var(--radius);
  padding: 1.15rem 1.2rem 1.05rem;
  min-height: 8.5rem;
  box-shadow: var(--shadow);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.kicker {
  font-size: 0.92rem;
  font-weight: 700;
  opacity: 0.95;
}

.figure {
  font-size: 2.1rem;
  font-weight: 800;
  letter-spacing: -0.03em;
}

span {
  font-size: 0.95rem;
  font-weight: 600;
  margin-left: 0.15rem;
}
</style>
