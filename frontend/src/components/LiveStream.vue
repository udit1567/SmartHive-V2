<script setup>
import { onUnmounted, ref, watch } from "vue";

import { request } from "@/api/client";
import { useAuthStore } from "@/stores/auth";

const props = defineProps({
  title: { type: String, required: true },
  detectPath: { type: String, required: true },
  countKey: { type: String, required: true },
});

const auth = useAuthStore();
const mode = ref("webcam");
const streamUrl = ref("");
const running = ref(false);
const busy = ref(false);
const error = ref("");
const detections = ref([]);
const count = ref(0);
const videoEl = ref(null);
const imgEl = ref(null);
const stageEl = ref(null);
const canvasEl = ref(null);
const frameSize = ref({ width: 0, height: 0 });

let mediaStream = null;
let loopTimer = 0;
let inFlight = false;

watch(detections, drawBoxes, { deep: true });

function drawBoxes() {
  const canvas = canvasEl.value;
  const stage = stageEl.value;
  const source = mode.value === "webcam" ? videoEl.value : imgEl.value;
  if (!canvas || !stage) {
    return;
  }
  const width = stage.clientWidth;
  const height =
    source?.clientHeight || source?.videoHeight || stage.clientHeight || 240;
  if (!width || !height) {
    return;
  }
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, width, height);
  const srcW = frameSize.value.width || source?.videoWidth || source?.naturalWidth || width;
  const srcH = frameSize.value.height || source?.videoHeight || source?.naturalHeight || height;
  const scaleX = width / srcW;
  const scaleY = height / srcH;
  ctx.strokeStyle = "#006d77";
  ctx.fillStyle = "#006d77";
  ctx.lineWidth = 2;
  ctx.font = "600 13px Nunito, sans-serif";
  for (const item of detections.value) {
    const [x1, y1, x2, y2] = item.box || [];
    if (x2 == null) {
      continue;
    }
    const x = x1 * scaleX;
    const y = y1 * scaleY;
    const w = (x2 - x1) * scaleX;
    const h = (y2 - y1) * scaleY;
    ctx.strokeRect(x, y, w, h);
    const label = `${item["class"]} ${Math.round(item.confidence * 100)}%`;
    ctx.fillRect(x, Math.max(0, y - 18), Math.min(ctx.measureText(label).width + 10, w || 120), 18);
    ctx.fillStyle = "#fff";
    ctx.fillText(label, x + 5, Math.max(12, y - 5));
    ctx.fillStyle = "#006d77";
  }
}

async function grabWebcamFrame() {
  const video = videoEl.value;
  if (!video || video.readyState < 2 || !video.videoWidth) {
    return null;
  }
  const scratch = document.createElement("canvas");
  const maxW = 640;
  const scale = Math.min(1, maxW / video.videoWidth);
  scratch.width = Math.round(video.videoWidth * scale);
  scratch.height = Math.round(video.videoHeight * scale);
  scratch.getContext("2d").drawImage(video, 0, 0, scratch.width, scratch.height);
  return new Promise((resolve) => scratch.toBlob((blob) => resolve(blob), "image/jpeg", 0.7));
}

async function detectOnce() {
  if (inFlight || !running.value) {
    return;
  }
  inFlight = true;
  busy.value = true;
  try {
    let data;
    if (mode.value === "webcam") {
      const blob = await grabWebcamFrame();
      if (!blob) {
        return;
      }
      const body = new FormData();
      body.append("image", blob, "frame.jpg");
      data = await request(props.detectPath, {
        method: "POST",
        deviceToken: auth.deviceToken,
        form: body,
      });
    } else {
      data = await request(props.detectPath, {
        method: "POST",
        deviceToken: auth.deviceToken,
        json: { source_url: streamUrl.value.trim() },
      });
    }
    detections.value = data.detections || [];
    count.value = data[props.countKey] ?? detections.value.length;
    if (data.width && data.height) {
      frameSize.value = { width: data.width, height: data.height };
    }
    error.value = "";
    requestAnimationFrame(drawBoxes);
  } catch (err) {
    error.value = err.message;
  } finally {
    inFlight = false;
    busy.value = false;
  }
}

function scheduleLoop() {
  const delay = mode.value === "webcam" ? 450 : 900;
  loopTimer = window.setTimeout(async () => {
    await detectOnce();
    if (running.value) {
      scheduleLoop();
    }
  }, delay);
}

async function startWebcam() {
  try {
    mediaStream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: "environment" },
      audio: false,
    });
  } catch {
    mediaStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
  }
  if (videoEl.value) {
    videoEl.value.srcObject = mediaStream;
    await videoEl.value.play();
  }
}

function stopMedia() {
  if (mediaStream) {
    mediaStream.getTracks().forEach((track) => track.stop());
    mediaStream = null;
  }
  if (videoEl.value) {
    videoEl.value.srcObject = null;
  }
}

async function start() {
  error.value = "";
  if (mode.value === "url" && !streamUrl.value.trim()) {
    error.value = "Paste a camera snapshot or MJPEG URL first.";
    return;
  }
  try {
    if (mode.value === "webcam") {
      await startWebcam();
    } else {
      stopMedia();
    }
    running.value = true;
    await detectOnce();
    scheduleLoop();
  } catch (err) {
    error.value = err.message || "Could not start the camera.";
    running.value = false;
  }
}

function stop() {
  running.value = false;
  window.clearTimeout(loopTimer);
  stopMedia();
  if (videoEl.value) {
    videoEl.value.removeAttribute("src");
  }
}

function setMode(next) {
  stop();
  mode.value = next;
}

onUnmounted(stop);
</script>

<template>
  <section class="live">
    <header>
      <h2>{{ title }}</h2>
      <p>Use this laptop’s webcam, or paste an HTTP snapshot / MJPEG URL from a hive camera.</p>
    </header>

    <div class="modes">
      <button type="button" :class="{ on: mode === 'webcam' }" @click="setMode('webcam')">
        Laptop webcam
      </button>
      <button type="button" :class="{ on: mode === 'url' }" @click="setMode('url')">
        Camera URL
      </button>
    </div>

    <label v-if="mode === 'url'" class="url">
      Stream URL
      <input
        v-model="streamUrl"
        type="url"
        placeholder="http://192.168.1.20/snapshot.jpg"
        :disabled="running"
      />
    </label>

    <div class="stage" ref="stageEl">
      <video v-show="mode === 'webcam'" ref="videoEl" autoplay playsinline muted></video>
      <img
        v-if="mode === 'url' && streamUrl"
        ref="imgEl"
        :src="streamUrl"
        alt="Camera stream"
      />
      <canvas ref="canvasEl"></canvas>
      <p v-if="!running" class="idle">Start the live stream to run detection on each frame.</p>
    </div>

    <div class="actions">
      <button v-if="!running" type="button" class="go" @click="start">Start live detection</button>
      <button v-else type="button" class="stop" @click="stop">Stop</button>
      <span v-if="running">{{ busy ? "Reading frame…" : `${count} live hits` }}</span>
    </div>

    <p v-if="error" class="err">{{ error }}</p>

    <ul v-if="detections.length">
      <li v-for="(item, index) in detections" :key="index">
        {{ item["class"] }}
        <span>{{ (item.confidence * 100).toFixed(0) }}%</span>
      </li>
    </ul>
  </section>
</template>

<style scoped>
.live {
  background: #fff;
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 1.2rem 1.25rem 1.3rem;
  margin-bottom: 1.25rem;
}

header p {
  color: var(--muted);
  margin-top: 0.3rem;
}

h2 {
  font-size: 1.2rem;
}

.modes {
  display: flex;
  gap: 0.5rem;
  margin: 1rem 0 0.85rem;
}

.modes button {
  border: 1px solid var(--line);
  background: var(--oasis-mist);
  border-radius: 999px;
  padding: 0.4rem 0.9rem;
  font-weight: 700;
  color: var(--muted);
}

.modes button.on {
  background: var(--oasis-teal);
  border-color: var(--oasis-teal);
  color: #fff;
}

.url {
  display: grid;
  gap: 0.35rem;
  font-size: 0.8rem;
  font-weight: 800;
  color: var(--muted);
  margin-bottom: 0.9rem;
}

.url input {
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 0.65rem 0.75rem;
  font-weight: 600;
}

.stage {
  position: relative;
  background: #12363a;
  border-radius: 12px;
  min-height: 240px;
  overflow: hidden;
}

video,
img,
canvas {
  width: 100%;
  display: block;
}

img {
  max-height: 420px;
  object-fit: contain;
  background: #0b2427;
}

canvas {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.idle {
  position: absolute;
  inset: 0;
  display: grid;
  place-items: center;
  color: #d7ecec;
  text-align: center;
  padding: 1rem;
  pointer-events: none;
}

.actions {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  margin-top: 0.9rem;
}

.go,
.stop {
  border: 0;
  border-radius: 8px;
  padding: 0.65rem 1rem;
  font-weight: 800;
  color: #fff;
}

.go {
  background: var(--oasis-teal);
}

.stop {
  background: var(--danger);
}

.err {
  color: var(--danger);
  margin-top: 0.7rem;
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
  padding: 0.5rem 0;
  font-weight: 700;
}

span {
  color: var(--muted);
  font-weight: 600;
}
</style>
