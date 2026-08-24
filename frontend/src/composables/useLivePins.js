import { computed } from "vue";

import { useDashboardStore } from "@/stores/dashboard";
import { useSensorStore } from "@/stores/sensors";

export function useLivePins() {
  const sensors = useSensorStore();
  const dashboard = useDashboardStore();

  const historyByPin = computed(() => {
    const map = {};
    for (const row of sensors.series) {
      for (const [key, value] of Object.entries(row)) {
        if (!key.startsWith("D") || typeof value !== "number") {
          continue;
        }
        (map[key] ??= []).push(value);
      }
    }
    return map;
  });

  function reading(pin) {
    const value = sensors.latestByKey[pin];
    return value === null || value === undefined ? null : value;
  }

  return { sensors, dashboard, historyByPin, reading };
}
