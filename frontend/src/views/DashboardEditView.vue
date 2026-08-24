<script setup>
import { ref } from "vue";

import WidgetCard from "@/components/WidgetCard.vue";
import WidgetSettings from "@/components/WidgetSettings.vue";
import { WIDGET_TYPES } from "@/constants/pins";
import { useLivePins } from "@/composables/useLivePins";

const { dashboard, historyByPin, reading } = useLivePins();
const editing = ref(null);
const dropActive = ref(false);

function onPaletteDrag(event, type) {
  event.dataTransfer.setData("text/widget-type", type);
  event.dataTransfer.effectAllowed = "copy";
}

function onCanvasDragOver(event) {
  event.preventDefault();
  dropActive.value = true;
}

function onCanvasDrop(event) {
  event.preventDefault();
  dropActive.value = false;
  const type = event.dataTransfer.getData("text/widget-type");
  const from = event.dataTransfer.getData("text/widget-index");
  if (type) {
    editing.value = dashboard.addWidget(type);
    return;
  }
  if (from !== "") {
    dashboard.moveWidget(Number(from), dashboard.widgets.length - 1);
  }
}

function onWidgetDragStart(event, index) {
  event.dataTransfer.setData("text/widget-index", String(index));
  event.dataTransfer.effectAllowed = "move";
}

function onWidgetDrop(event, index) {
  event.preventDefault();
  event.stopPropagation();
  const from = event.dataTransfer.getData("text/widget-index");
  if (from !== "") {
    dashboard.moveWidget(Number(from), index);
  }
}

function addFromClick(type) {
  editing.value = dashboard.addWidget(type);
}
</script>

<template>
  <section>
    <header>
      <div>
        <h1>Edit dashboard</h1>
        <p>Drag widgets from the box, then bind each one to a pin like D1 or D2.</p>
      </div>
      <router-link :to="{ name: 'overview' }">Back to dashboard</router-link>
    </header>

    <div class="workspace">
      <aside>
        <h2>Widget box</h2>
        <button
          v-for="item in WIDGET_TYPES"
          :key="item.type"
          type="button"
          draggable="true"
          @dragstart="onPaletteDrag($event, item.type)"
          @click="addFromClick(item.type)"
        >
          <strong>{{ item.label }}</strong>
          <span>{{ item.hint }}</span>
        </button>
      </aside>

      <div
        class="canvas"
        :class="{ active: dropActive }"
        @dragover="onCanvasDragOver"
        @dragleave="dropActive = false"
        @drop="onCanvasDrop"
      >
        <p v-if="!dashboard.widgets.length" class="empty">
          Drop a widget here. Example: labeled value → pin D1 → name it Temperature.
        </p>
        <WidgetCard
          v-for="(widget, index) in dashboard.widgets"
          :key="widget.id"
          editable
          :widget="widget"
          :value="reading(widget.pin)"
          :history="historyByPin[widget.pin] || []"
          draggable="true"
          @dragstart="onWidgetDragStart($event, index)"
          @dragover.prevent
          @drop="onWidgetDrop($event, index)"
          @edit="editing = widget"
          @remove="dashboard.removeWidget(widget.id)"
        />
      </div>
    </div>

    <WidgetSettings
      v-if="editing"
      :widget="editing"
      @close="editing = null"
      @save="dashboard.updateWidget(editing.id, $event); editing = null"
    />
  </section>
</template>

<style scoped>
header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 1rem;
  margin-bottom: 1.2rem;
}

h1 {
  font-size: 1.9rem;
  font-weight: 800;
}

header p {
  color: var(--muted);
  max-width: 42rem;
  margin-top: 0.35rem;
}

header a {
  color: var(--oasis-teal);
  font-weight: 800;
}

.workspace {
  display: grid;
  grid-template-columns: 220px 1fr;
  gap: 1rem;
  align-items: start;
}

aside {
  background: #fff;
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 1rem 0.85rem;
  display: grid;
  gap: 0.65rem;
}

h2 {
  font-size: 0.8rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--muted);
}

aside button {
  text-align: left;
  border: 1px dashed var(--oasis-water);
  background: var(--oasis-mist);
  border-radius: 10px;
  padding: 0.75rem 0.8rem;
  cursor: grab;
}

aside button span {
  display: block;
  margin-top: 0.2rem;
  color: var(--muted);
  font-size: 0.78rem;
}

.canvas {
  min-height: 28rem;
  background: #fff;
  border: 2px dashed var(--line);
  border-radius: var(--radius);
  padding: 1rem;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 1rem;
  align-content: start;
}

.canvas.active {
  border-color: var(--oasis-teal);
  background: #f3fbfb;
}

.empty {
  grid-column: 1 / -1;
  color: var(--muted);
  padding: 4rem 1rem;
  text-align: center;
}

@media (max-width: 840px) {
  .workspace {
    grid-template-columns: 1fr;
  }
}
</style>
