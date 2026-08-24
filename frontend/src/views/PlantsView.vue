<script setup>
import DetectPanel from "@/components/DetectPanel.vue";
</script>

<template>
  <DetectPanel
    title="The leaf, observed."
    detect-path="/detect_plant_disease"
    fetch-path="/fetch_plant_disease_images"
    images-key="plant_disease_images"
    count-key="total_diseases_detected"
  />
</template>
