<script setup>
import { computed } from "vue";

import SparkLine from "@/components/SparkLine.vue";

const props = defineProps({
  widget: { type: Object, required: true },
  value: { type: [Number, String], default: null },
  history: { type: Array, default: () => [] },
  editable: { type: Boolean, default: false },
});

defineEmits(["edit", "remove", "drag-start"]);

const display = computed(() => {
  if (props.value === null || props.value === undefined) {
    return "—";
  }
  return Number(props.value).toFixed(1);
});

const percent = computed(() => {
  const min = Number(props.widget.min) || 0;
  const max = Number(props.widget.max) || 100;
  const span = max - min || 1;
  const raw = ((Number(props.value) - min) / span) * 100;
  return Math.min(100, Math.max(0, Number.isFinite(raw) ? raw : 0));
});
</script>

<template>
  <article class="card" :style="{ '--accent': widget.color }">
    <header>
      <button
        v-if="editable"
        class="handle"
        type="button"
        title="Drag to reorder"
        @mousedown="$emit('drag-start')"
      >
        ⋮⋮
      </button>
      <div>
        <p class="title">{{ widget.title }}</p>
        <p class="pin">{{ widget.pin }}</p>
      </div>
      <template v-if="editable">
        <button type="button" class="icon" @click="$emit('edit')">Edit</button>
        <button type="button" class="icon" @click="$emit('remove')">✕</button>
      </template>
    </header>

    <div v-if="widget.type === 'value'" class="value">
      {{ display }}
      <span v-if="widget.unit">{{ widget.unit }}</span>
    </div>

    <div v-else-if="widget.type === 'gauge'" class="gauge">
      <div
        class="ring"
        :style="{ background: `conic-gradient(var(--accent) ${percent}%, #d5e4e6 0)` }"
      >
        <div class="hole">
          {{ display }}
          <small>{{ widget.unit }}</small>
        </div>
      </div>
    </div>

    <SparkLine v-else :values="history" :color="widget.color" />
  </article>
</template>

<style scoped>
.card {
  background: #fff;
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 0.9rem 1rem 1rem;
  min-height: 11rem;
}

header {
  display: grid;
  grid-template-columns: 1fr auto auto;
  gap: 0.4rem;
  align-items: start;
}

.card:has(.handle) header {
  grid-template-columns: auto 1fr auto auto;
}

.title {
  font-weight: 800;
}

.pin {
  color: var(--muted);
  font-size: 0.75rem;
  letter-spacing: 0.08em;
}

.handle,
.icon {
  background: none;
  border: 0;
  color: var(--muted);
  padding: 0.15rem 0.3rem;
}

.handle {
  cursor: grab;
}

.value {
  margin-top: 1.4rem;
  font-size: 2.4rem;
  font-weight: 800;
  color: var(--accent);
}

.value span {
  font-size: 1rem;
  margin-left: 0.2rem;
}

.gauge {
  display: grid;
  place-items: center;
  margin-top: 0.6rem;
}

.ring {
  width: 7.2rem;
  height: 7.2rem;
  border-radius: 50%;
  display: grid;
  place-items: center;
}

.hole {
  width: 5.2rem;
  height: 5.2rem;
  border-radius: 50%;
  background: #fff;
  display: grid;
  place-content: center;
  text-align: center;
  font-weight: 800;
  font-size: 1.35rem;
}

small {
  display: block;
  color: var(--muted);
  font-weight: 600;
}
</style>
