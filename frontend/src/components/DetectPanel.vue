<script setup>
import { onMounted, ref } from "vue";

import { request } from "@/api/client";
import AppButton from "@/components/AppButton.vue";
import { useAuthStore } from "@/stores/auth";

const props = defineProps({
  title: { type: String, required: true },
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
    error.value = "Choose a still first.";
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
      <p class="eyebrow">Studio</p>
      <h1>{{ title }}</h1>
    </header>

    <form @submit.prevent="detect">
      <label class="drop">
        <input type="file" accept="image/*" @change="onFile" />
        <span>{{ file ? file.name : "Place a photograph" }}</span>
      </label>
      <img v-if="preview" :src="preview" alt="Selected still" />
      <AppButton label="Read the image" :busy="busy" />
    </form>

    <p v-if="error" class="err">{{ error }}</p>

    <div v-if="result" class="result">
      <p>{{ result[countKey] ?? 0 }} findings</p>
      <ul>
        <li v-for="(item, index) in result.detections || []" :key="index">
          {{ item["class"] }}
          <span>{{ (item.confidence * 100).toFixed(0) }}%</span>
        </li>
      </ul>
    </div>

    <div class="gallery" v-if="images.length">
      <img v-for="src in images" :key="src" :src="src" alt="Prior detection" />
    </div>
  </section>
</template>

<style scoped>
header {
  margin-bottom: 2rem;
}

.eyebrow {
  letter-spacing: 0.18em;
  text-transform: uppercase;
  font-size: 0.7rem;
  color: var(--muted);
}

h1 {
  font-size: clamp(2.4rem, 5vw, 3.8rem);
  margin-top: 0.35rem;
}

form {
  display: grid;
  gap: 1.2rem;
  max-width: 28rem;
}

.drop {
  border-bottom: 1px solid var(--line);
  padding: 1rem 0;
  cursor: pointer;
}

.drop input {
  display: none;
}

img {
  width: min(100%, 28rem);
  height: auto;
  object-fit: cover;
  filter: grayscale(0.15);
}

.err {
  color: var(--danger);
  margin-top: 1rem;
}

.result {
  margin-top: 2rem;
  max-width: 28rem;
}

ul {
  list-style: none;
  padding: 0;
  margin: 0.8rem 0 0;
}

li {
  display: flex;
  justify-content: space-between;
  border-top: 1px solid var(--line);
  padding: 0.55rem 0;
}

.gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 0.75rem;
  margin-top: 2.5rem;
}

.gallery img {
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
}
</style>
