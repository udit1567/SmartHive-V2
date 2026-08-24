<script setup>
import { reactive, watch } from "vue";

import { PINS, WIDGET_COLORS } from "@/constants/pins";

const props = defineProps({
  widget: { type: Object, required: true },
});

const emit = defineEmits(["save", "close"]);
const form = reactive({ ...props.widget });

watch(
  () => props.widget,
  (next) => Object.assign(form, next)
);

function submit() {
  emit("save", {
    title: form.title,
    pin: form.pin,
    unit: form.unit,
    min: Number(form.min),
    max: Number(form.max),
    color: form.color,
  });
}
</script>

<template>
  <div class="mask" @click.self="$emit('close')">
    <form class="sheet" @submit.prevent="submit">
      <h2>Widget settings</h2>
      <p>Bind this card to a datastream pin, the same way Blynk uses V pins.</p>

      <label>
        Name
        <input v-model="form.title" required />
      </label>
      <label>
        Datastream
        <select v-model="form.pin">
          <option v-for="pin in PINS" :key="pin" :value="pin">{{ pin }}</option>
        </select>
      </label>
      <label>
        Unit
        <input v-model="form.unit" placeholder="°C, %, lux…" />
      </label>
      <div class="row" v-if="widget.type === 'gauge'">
        <label>
          Min
          <input v-model="form.min" type="number" />
        </label>
        <label>
          Max
          <input v-model="form.max" type="number" />
        </label>
      </div>
      <label>
        Color
        <select v-model="form.color">
          <option v-for="swatch in WIDGET_COLORS" :key="swatch.id" :value="swatch.value">
            {{ swatch.label }}
          </option>
        </select>
      </label>

      <div class="actions">
        <button type="button" class="ghost" @click="$emit('close')">Cancel</button>
        <button type="submit">Save</button>
      </div>
    </form>
  </div>
</template>

<style scoped>
.mask {
  position: fixed;
  inset: 0;
  background: rgba(26, 60, 64, 0.35);
  display: grid;
  place-items: center;
  z-index: 20;
  padding: 1rem;
}

.sheet {
  width: min(100%, 420px);
  background: #fff;
  border-radius: 16px;
  padding: 1.4rem;
  display: grid;
  gap: 0.85rem;
}

h2 {
  font-size: 1.3rem;
}

p {
  color: var(--muted);
  font-size: 0.9rem;
}

label {
  display: grid;
  gap: 0.35rem;
  font-size: 0.8rem;
  font-weight: 700;
}

input,
select {
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 0.65rem 0.7rem;
  font-weight: 500;
}

.row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.8rem;
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.6rem;
  margin-top: 0.4rem;
}

button {
  border: 0;
  border-radius: 8px;
  padding: 0.65rem 1rem;
  font-weight: 800;
  background: var(--oasis-teal);
  color: #fff;
}

.ghost {
  background: transparent;
  color: var(--muted);
}
</style>
