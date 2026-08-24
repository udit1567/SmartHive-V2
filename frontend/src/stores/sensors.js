import { defineStore } from "pinia";
import { computed, ref } from "vue";

import { PINS } from "@/constants/pins";
import { ApiError, request } from "@/api/client";
import { useAuthStore } from "@/stores/auth";

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
        ...PINS.map((pin) =>
          request(`/get_${pin.toLowerCase()}/${auth.uid}`).catch(() => null)
        ),
      ]);
      series.value = history.data ?? [];
      latestByKey.value = PINS.reduce((acc, pin, index) => {
        const payload = points[index];
        acc[pin] = payload ? payload[pin] : null;
        return acc;
      }, {});
    } catch (err) {
      error.value = err.message;
      series.value = [];
    } finally {
      loading.value = false;
    }
  }

  let pollTimer = null;

  function startPolling(ms = 15000) {
    if (pollTimer) {
      return;
    }
    refresh();
    pollTimer = setInterval(() => {
      refresh();
    }, ms);
  }

  function stopPolling() {
    clearInterval(pollTimer);
    pollTimer = null;
  }

  return { series, latestByKey, latest, loading, error, refresh, startPolling, stopPolling };
});
