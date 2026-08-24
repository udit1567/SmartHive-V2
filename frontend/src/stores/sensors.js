import { defineStore } from "pinia";
import { computed, ref } from "vue";

import { ApiError, request } from "@/api/client";
import { useAuthStore } from "@/stores/auth";

export const SENSOR_META = [
  { key: "D1", label: "Temperature", unit: "°C" },
  { key: "D2", label: "Humidity", unit: "%" },
  { key: "D3", label: "Soil moisture", unit: "%" },
  { key: "D4", label: "Air quality", unit: "AQI" },
  { key: "D5", label: "Light", unit: "lx" },
  { key: "D6", label: "Pressure", unit: "hPa" },
  { key: "D7", label: "Voltage", unit: "V" },
  { key: "D8", label: "Auxiliary", unit: "" },
];

export const useSensorStore = defineStore("sensors", () => {
  const series = ref([]);
  const latestByKey = ref({});
  const loading = ref(false);
  const error = ref("");

  const latest = computed(() => series.value.at(-1) ?? null);

  async function refresh() {
    const auth = useAuthStore();
    if (!auth.uid) {
      return;
    }
    loading.value = true;
    error.value = "";
    try {
      const [history, ...points] = await Promise.all([
        request(`/get_data/${auth.uid}`).catch((err) => {
          if (err instanceof ApiError && err.status === 404) {
            return { data: [] };
          }
          throw err;
        }),
        ...SENSOR_META.map((sensor) =>
          request(`/get_${sensor.key.toLowerCase()}/${auth.uid}`).catch(() => null)
        ),
      ]);
      series.value = history.data ?? [];
      latestByKey.value = SENSOR_META.reduce((acc, sensor, index) => {
        const payload = points[index];
        acc[sensor.key] = payload ? payload[sensor.key] : null;
        return acc;
      }, {});
    } catch (err) {
      error.value = err.message;
      series.value = [];
    } finally {
      loading.value = false;
    }
  }

  return { series, latestByKey, latest, loading, error, refresh };
});
