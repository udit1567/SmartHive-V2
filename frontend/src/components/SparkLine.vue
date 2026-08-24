<script setup>
import { computed } from "vue";

const props = defineProps({
  values: { type: Array, default: () => [] },
  color: { type: String, default: "#006d77" },
});

const path = computed(() => {
  const nums = props.values.filter((n) => typeof n === "number");
  if (nums.length < 2) {
    return "";
  }
  const min = Math.min(...nums);
  const max = Math.max(...nums);
  const span = max - min || 1;
  return nums
    .map((value, index) => {
      const x = (index / (nums.length - 1)) * 100;
      const y = 38 - ((value - min) / span) * 30;
      return `${index === 0 ? "M" : "L"}${x.toFixed(2)},${y.toFixed(2)}`;
    })
    .join(" ");
});
</script>

<template>
  <svg viewBox="0 0 100 42" preserveAspectRatio="none" aria-hidden="true">
    <path v-if="path" :d="path" :stroke="color" />
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
  stroke-width: 1.6;
  stroke-linecap: round;
}
</style>
