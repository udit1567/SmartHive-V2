import { defineStore } from "pinia";
import { ref, watch } from "vue";

import { useAuthStore } from "@/stores/auth";

function storageKey(uid) {
  return `smarthive.widgets.${uid}`;
}

function createWidget(type, pin = "D1") {
  return {
    id: crypto.randomUUID(),
    type,
    pin,
    title: type === "chart" ? `${pin} chart` : pin,
    unit: "",
    min: 0,
    max: 100,
    color: "#006d77",
  };
}

export const useDashboardStore = defineStore("dashboard", () => {
  const widgets = ref([]);

  function load() {
    const auth = useAuthStore();
    if (!auth.uid) {
      widgets.value = [];
      return;
    }
    try {
      const raw = localStorage.getItem(storageKey(auth.uid));
      widgets.value = raw ? JSON.parse(raw) : [];
    } catch {
      widgets.value = [];
    }
  }

  function save() {
    const auth = useAuthStore();
    if (!auth.uid) {
      return;
    }
    localStorage.setItem(storageKey(auth.uid), JSON.stringify(widgets.value));
  }

  function addWidget(type, pin = "D1") {
    const widget = createWidget(type, pin);
    widgets.value.push(widget);
    save();
    return widget;
  }

  function updateWidget(id, patch) {
    widgets.value = widgets.value.map((widget) =>
      widget.id === id ? { ...widget, ...patch } : widget
    );
    save();
  }

  function removeWidget(id) {
    widgets.value = widgets.value.filter((widget) => widget.id !== id);
    save();
  }

  function moveWidget(fromIndex, toIndex) {
    if (fromIndex === toIndex || fromIndex < 0 || toIndex < 0) {
      return;
    }
    const next = [...widgets.value];
    const [item] = next.splice(fromIndex, 1);
    next.splice(toIndex, 0, item);
    widgets.value = next;
    save();
  }

  watch(widgets, save, { deep: true });

  return {
    widgets,
    load,
    addWidget,
    updateWidget,
    removeWidget,
    moveWidget,
  };
});
