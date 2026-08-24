<script setup>
import DetectPanel from "@/components/DetectPanel.vue";
import LiveStream from "@/components/LiveStream.vue";
</script>

<template>
  <div>
    <LiveStream
      title="Live object detection"
      detect-path="/detect_live_objects"
      count-key="total_objects"
    />
    <DetectPanel
      title="Object Detection"
      subtitle="Upload a still from the hive camera."
      detect-path="/detect_objects"
      fetch-path="/fetch_object_detection_images"
      images-key="object_detection_images"
      count-key="total_objects"
    />
  </div>
</template>
