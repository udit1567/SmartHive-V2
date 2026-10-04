<script setup>
import { computed, onMounted, ref } from "vue";

import { request } from "@/api/client";
import AppButton from "@/components/AppButton.vue";
import { useAuthStore } from "@/stores/auth";

const props = defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: "" },
  detectPath: { type: String, required: true },
  fetchPath: { type: String, required: true },
  imagesKey: { type: String, required: true },
  countKey: { type: String, required: true },
});

const emit = defineEmits(["detected"]);

const auth = useAuthStore();
const file = ref(null);
const preview = ref("");
const result = ref(null);
const images = ref([]);
const error = ref("");
const busy = ref(false);

function onFile(event) {
  const next = event.target.files?.[0];
  file.value = next || null;
  preview.value = next ? URL.createObjectURL(next) : "";
}

async function loadImages() {
  try {
    const data = await request(props.fetchPath, { deviceToken: auth.deviceToken });
    images.value = data[props.imagesKey] ?? [];
  } catch (err) {
    error.value = err.message;
  }
}

async function detect() {
  if (!file.value) {
    error.value = "Choose an image first.";
    return;
  }
  error.value = "";
  busy.value = true;
  const body = new FormData();
  body.append("image", file.value);
  try {
    result.value = await request(props.detectPath, {
      method: "POST",
      deviceToken: auth.deviceToken,
      form: body,
    });
    emit("detected", result.value);
    await loadImages();
  } catch (err) {
    error.value = err.message;
  } finally {
    busy.value = false;
  }
}

onMounted(loadImages);

// Collapse repeated boxes of the same class (e.g. several overlapping leaf
// regions all tagged "Apple Scab Leaf") into one row with a count, instead
// of a long list of near-duplicate entries.
const groupedDetections = computed(() => {
  const grouped = new Map();
  for (const item of result.value?.detections || []) {
    const cls = item["class"];
    const entry = grouped.get(cls);
    if (entry) {
      entry.count += 1;
      entry.confidence = Math.max(entry.confidence, item.confidence);
    } else {
      grouped.set(cls, { class: cls, count: 1, confidence: item.confidence });
    }
  }
  return [...grouped.values()].sort((a, b) => b.confidence - a.confidence);
});
</script>

<template>
  <section>
    <header>
      <h1>{{ title }}</h1>
      <p v-if="subtitle">{{ subtitle }}</p>
    </header>

    <div class="panel">
      <form @submit.prevent="detect">
        <label class="drop">
          <input type="file" accept="image/*" @change="onFile" />
          <span>{{ file ? file.name : "Upload an image" }}</span>
        </label>
        <img v-if="preview" :src="preview" alt="Selected upload" />
        <AppButton label="Detect" :busy="busy" />
        <p v-if="error" class="err">{{ error }}</p>
      </form>

      <div v-if="result" class="result">
        <h2>{{ result[countKey] ?? 0 }} detections</h2>
        <ul>
          <li v-for="item in groupedDetections" :key="item.class">
            {{ item.class }}
            <span>{{ item.count > 1 ? `${item.count}× · ` : "" }}{{ (item.confidence * 100).toFixed(0) }}%</span>
          </li>
        </ul>
      </div>
    </div>

    <div class="gallery" v-if="images.length">
      <img v-for="src in images" :key="src" :src="src" alt="Saved detection" />
    </div>
  </section>
</template>

<style scoped>
header {
  margin-bottom: 1.2rem;
}

h1 {
  font-size: 1.8rem;
  font-weight: 800;
}

header p {
  color: var(--muted);
}

.panel {
  background: #fff;
  border-radius: var(--radius);
  padding: 1.25rem;
  box-shadow: var(--shadow);
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  gap: 1.25rem;
}

form {
  display: grid;
  gap: 1rem;
  flex: 1 1 20rem;
  min-width: 0;
}

.drop {
  border: 1px dashed var(--oasis-water);
  border-radius: 10px;
  padding: 1.1rem;
  text-align: center;
  cursor: pointer;
  background: var(--oasis-mist);
  font-weight: 700;
  color: var(--brand);
}

.drop input {
  display: none;
}

img {
  width: 100%;
  border-radius: 10px;
  object-fit: cover;
}

.err {
  color: var(--danger);
  margin-top: 0.8rem;
}

.result {
  flex: 1 1 16rem;
  min-width: 0;
}

h2 {
  font-size: 1rem;
}

ul {
  list-style: none;
  padding: 0;
  margin: 0.5rem 0 0;
}

li {
  display: flex;
  justify-content: space-between;
  border-top: 1px solid var(--line);
  padding: 0.55rem 0;
}

.gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 0.75rem;
  margin-top: 1.25rem;
}

.gallery img {
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
  border-radius: 10px;
  box-shadow: var(--shadow);
}
</style>
