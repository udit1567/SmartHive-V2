<script setup>
import DetectPanel from "@/components/DetectPanel.vue";
import LiveStream from "@/components/LiveStream.vue";
import MoistureGraph from "@/components/MoistureGraph.vue";
</script>

<template>
  <div>
    <MoistureGraph />
    <LiveStream
      title="Live plant detection"
      detect-path="/detect_live_plant_disease"
      count-key="total_diseases_detected"
    />
    <DetectPanel
      title="Plant Health"
      subtitle="Upload a leaf photo to check for disease."
      detect-path="/detect_plant_disease"
      fetch-path="/fetch_plant_disease_images"
      images-key="plant_disease_images"
      count-key="total_diseases_detected"
    />
  </div>
</template>
