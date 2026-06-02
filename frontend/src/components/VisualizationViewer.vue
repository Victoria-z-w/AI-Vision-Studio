<template>
  <div class="vis-viewer">
    <YoloOverlay
      v-if="model === 'yolo' && detections"
      :image-url="imageUrl"
      :detections="detections"
    />
    <OcrOverlay
      v-else-if="model === 'ocr' && regions"
      :image-url="imageUrl"
      :regions="regions"
    />
    <RembgCompare
      v-else-if="model === 'rembg'"
      :original-url="imageUrl"
      :foreground-url="foregroundUrl"
      :foreground-base64="foregroundBase64"
    />
    <el-empty v-else description="No visualization available" :image-size="80" />
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { Detection, OCRRegion } from "@/types";
import YoloOverlay from "./YoloOverlay.vue";
import OcrOverlay from "./OcrOverlay.vue";
import RembgCompare from "./RembgCompare.vue";
import { getVisualizationUrl, getForegroundUrl } from "@/api/tasks";

const props = defineProps<{
  taskId: string;
  model: string;
  result?: Record<string, unknown>;
  visBase64?: string;
  foregroundBase64?: string;
}>();

const imageUrl = computed(() => props.visBase64 || getVisualizationUrl(props.taskId));
const foregroundUrl = computed(() => props.foregroundBase64 || getForegroundUrl(props.taskId));

const detections = computed<Detection[] | null>(() => {
  if (props.model !== "yolo" || !props.result) return null;
  const r = props.result as { detections?: Detection[] };
  return r.detections || [];
});

const regions = computed<OCRRegion[] | null>(() => {
  if (props.model !== "ocr" || !props.result) return null;
  const r = props.result as { regions?: OCRRegion[] };
  return r.regions || [];
});
</script>

<style scoped>
.vis-viewer {
  width: 100%;
}
</style>
