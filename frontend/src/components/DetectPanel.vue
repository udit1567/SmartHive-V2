<script setup>
import { onMounted, ref } from "vue";

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
    await loadImages();
  } catch (err) {
    error.value = err.message;
  } finally {
    busy.value = false;
  }
}

onMounted(loadImages);
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
      </form>

      <p v-if="error" class="err">{{ error }}</p>

      <div v-if="result" class="result">
        <h2>{{ result[countKey] ?? 0 }} detections</h2>
        <ul>
          <li v-for="(item, index) in result.detections || []" :key="index">
            {{ item["class"] }}
            <span>{{ (item.confidence * 100).toFixed(0) }}%</span>
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
  max-width: 36rem;
}

form {
  display: grid;
  gap: 1rem;
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
  margin-top: 1.1rem;
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
