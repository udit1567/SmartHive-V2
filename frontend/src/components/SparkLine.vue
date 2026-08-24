<script setup>
import { computed } from "vue";

const props = defineProps({
  points: { type: Array, default: () => [] },
});

const path = computed(() => {
  const values = props.points.filter((n) => typeof n === "number");
  if (values.length < 2) {
    return "";
  }
  const min = Math.min(...values);
  const max = Math.max(...values);
  const span = max - min || 1;
  return values
    .map((value, index) => {
      const x = (index / (values.length - 1)) * 100;
      const y = 36 - ((value - min) / span) * 32;
      return `${index === 0 ? "M" : "L"}${x.toFixed(2)},${y.toFixed(2)}`;
    })
    .join(" ");
});
</script>

<template>
  <svg viewBox="0 0 100 40" preserveAspectRatio="none" aria-hidden="true">
    <path v-if="path" :d="path" />
  </svg>
</template>

<style scoped>
svg {
  width: 100%;
  height: 140px;
  display: block;
}

path {
  fill: none;
  stroke: var(--ink);
  stroke-width: 0.6;
}
</style>
