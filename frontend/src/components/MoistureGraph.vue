<script setup>
import { computed, ref, watch } from "vue";

import { PINS } from "@/constants/pins";
import { useLivePins } from "@/composables/useLivePins";

const STORAGE_KEY = "smarthive.soil-pin";
const { sensors, reading } = useLivePins();
const pin = ref(localStorage.getItem(STORAGE_KEY) || "D3");

watch(pin, (value) => localStorage.setItem(STORAGE_KEY, value));

const points = computed(() =>
  sensors.series
    .filter((row) => typeof row[pin.value] === "number")
    .map((row) => ({
      value: Math.max(0, Math.min(100, row[pin.value])),
      time: row.timestamp ? new Date(row.timestamp).toLocaleTimeString() : "",
    }))
);

const latest = computed(() => reading(pin.value));

const path = computed(() => {
  if (points.value.length < 2) {
    return "";
  }
  const width = 100;
  const height = 56;
  const last = points.value.length - 1;
  return points.value
    .map((point, index) => {
      const x = (index / last) * width;
      const y = height - (point.value / 100) * height;
      return `${index === 0 ? "M" : "L"}${x.toFixed(2)},${y.toFixed(2)}`;
    })
    .join(" ");
});

const area = computed(() => {
  if (!path.value) {
    return "";
  }
  return `${path.value} L100,56 L0,56 Z`;
});

const yTicks = [0, 25, 50, 75, 100];
</script>

<template>
  <article class="panel">
    <header>
      <div>
        <h2>Soil moisture</h2>
        <p>Trend from the pin your probe writes to. Default is D3, as in the original hive.</p>
      </div>
      <label>
        Pin
        <select v-model="pin">
          <option v-for="item in PINS" :key="item" :value="item">{{ item }}</option>
        </select>
      </label>
    </header>

    <p class="now">
      {{ latest === null ? "—" : Number(latest).toFixed(1) }}
      <span>%</span>
    </p>

    <div class="chart" v-if="points.length >= 2">
      <svg viewBox="-8 -4 116 72" preserveAspectRatio="none">
        <line
          v-for="tick in yTicks"
          :key="tick"
          x1="0"
          x2="100"
          :y1="56 - tick * 0.56"
          :y2="56 - tick * 0.56"
        />
        <path class="fill" :d="area" />
        <path class="line" :d="path" />
      </svg>
      <div class="axis">
        <span>{{ points[0].time }}</span>
        <span>Moisture 0–100</span>
        <span>{{ points.at(-1).time }}</span>
      </div>
    </div>
    <p v-else class="empty">No moisture history on {{ pin }} yet. Send readings to that pin from the device.</p>
  </article>
</template>

<style scoped>
.panel {
  background: #fff;
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 1.2rem 1.3rem 1.1rem;
  margin-bottom: 1.25rem;
}

header {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: flex-start;
}

h2 {
  font-size: 1.15rem;
}

header p {
  color: var(--muted);
  font-size: 0.9rem;
  margin-top: 0.25rem;
  max-width: 36rem;
}

label {
  display: grid;
  gap: 0.3rem;
  font-size: 0.75rem;
  font-weight: 800;
  color: var(--muted);
}

select {
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 0.45rem 0.55rem;
  min-width: 4.5rem;
}

.now {
  font-size: 2.4rem;
  font-weight: 800;
  color: var(--oasis-teal);
  margin: 0.8rem 0 0.6rem;
}

.now span {
  font-size: 1rem;
  color: var(--muted);
}

.chart {
  height: 240px;
}

svg {
  width: 100%;
  height: 210px;
  display: block;
}

line {
  stroke: var(--line);
  stroke-width: 0.4;
}

.fill {
  fill: rgba(0, 109, 119, 0.12);
  stroke: none;
}

.line {
  fill: none;
  stroke: var(--oasis-teal);
  stroke-width: 1.6;
  stroke-linecap: round;
}

.axis {
  display: flex;
  justify-content: space-between;
  color: var(--muted);
  font-size: 0.75rem;
}

.empty {
  color: var(--muted);
  padding: 1.5rem 0 0.4rem;
}
</style>
