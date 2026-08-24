<script setup>
import DetectPanel from "@/components/DetectPanel.vue";
</script>

<template>
  <DetectPanel
    title="What stands in the frame."
    detect-path="/detect_objects"
    fetch-path="/fetch_object_detection_images"
    images-key="object_detection_images"
    count-key="total_objects"
  />
</template>
