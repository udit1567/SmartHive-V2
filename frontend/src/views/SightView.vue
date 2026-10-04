<script setup>
import AiSurveillancePanel from "@/components/AiSurveillancePanel.vue";
import LiveStream from "@/components/LiveStream.vue";
</script>

<template>
  <div>
    <LiveStream
      title="Live object detection"
      detect-path="/detect_live_objects"
      stream-path="/stream_live_objects"
      count-key="total_objects"
    />
    <AiSurveillancePanel />
  </div>
</template>
