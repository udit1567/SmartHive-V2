<script setup>
import { computed, onMounted, onUnmounted } from "vue";

import MetricCard from "@/components/MetricCard.vue";
import SparkLine from "@/components/SparkLine.vue";
import { SENSOR_META, useSensorStore } from "@/stores/sensors";

const sensors = useSensorStore();
let timer;

const tempSeries = computed(() =>
  sensors.series.map((row) => row.D1).filter((n) => n !== null && n !== undefined)
);

function display(key) {
  const value = sensors.latestByKey[key];
  return value === null || value === undefined ? "—" : Number(value).toFixed(1);
}

onMounted(async () => {
  await sensors.refresh();
  timer = setInterval(() => sensors.refresh(), 20000);
});

onUnmounted(() => {
  clearInterval(timer);
});
</script>

<template>
  <section>
    <header>
      <p class="eyebrow">Now</p>
      <h1>The room, at rest.</h1>
      <p class="note" v-if="sensors.loading">Listening…</p>
      <p class="note" v-else-if="sensors.error">{{ sensors.error }}</p>
      <p class="note" v-else-if="!sensors.series.length">
        No readings yet. Pair a device and wait for the first pulse.
      </p>
    </header>

    <SparkLine :points="tempSeries" />

    <div class="grid">
      <MetricCard
        v-for="sensor in SENSOR_META"
        :key="sensor.key"
        :label="sensor.label"
        :value="display(sensor.key)"
        :unit="sensor.unit"
      />
    </div>
  </section>
</template>

<style scoped>
header {
  max-width: 36rem;
  margin-bottom: 2rem;
}

.eyebrow {
  letter-spacing: 0.18em;
  text-transform: uppercase;
  font-size: 0.7rem;
  color: var(--muted);
}

h1 {
  font-size: clamp(2.6rem, 5vw, 4.2rem);
  margin: 0.4rem 0 0.8rem;
}

.note {
  color: var(--muted);
}

.grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0 2rem;
  margin-top: 1.5rem;
}

@media (max-width: 980px) {
  .grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
