<script setup>
import { ref } from "vue";

import DetectPanel from "@/components/DetectPanel.vue";
import MoistureGraph from "@/components/MoistureGraph.vue";
import PlantAiChat from "@/components/PlantAiChat.vue";

const chatOpen = ref(false);
const refreshSignal = ref(0);

function onDetected() {
  refreshSignal.value += 1;
}

function toggleChat() {
  chatOpen.value = !chatOpen.value;
}
</script>

<template>
  <div>
    <header>
      <div>
        <h1>Agriculture Monitoring</h1>
        <p>Soil moisture, leaf disease detection, and history for this hive's plants.</p>
      </div>
      <button type="button" class="chat-toggle" @click="toggleChat">
        {{ chatOpen ? "Close AI chat" : "Consult AI" }}
      </button>
    </header>

    <template v-if="!chatOpen">
      <MoistureGraph />
      <DetectPanel
        title="Leaf disease detection"
        subtitle="Upload a leaf photo to check for disease."
        detect-path="/detect_plant_disease"
        fetch-path="/fetch_plant_disease_images"
        images-key="plant_disease_images"
        count-key="total_diseases_detected"
        @detected="onDetected"
      />
    </template>
    <PlantAiChat v-else :refresh-signal="refreshSignal" />
  </div>
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
  margin-top: 0.3rem;
}

.chat-toggle {
  border: 0;
  background: var(--oasis-teal);
  color: #fff;
  font-weight: 800;
  padding: 0.65rem 1rem;
  border-radius: 8px;
  flex: none;
}
</style>
