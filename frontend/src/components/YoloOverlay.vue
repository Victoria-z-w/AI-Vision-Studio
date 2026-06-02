<template>
  <div class="yolo-overlay">
    <div class="overlay-container" ref="containerRef">
      <img
        :src="imageUrl"
        ref="imgRef"
        class="base-image"
        @load="drawBoxes"
        alt="Detection result"
      />
      <canvas ref="canvasRef" class="overlay-canvas" />
    </div>
    <div v-if="detections.length === 0" class="no-result">
      <el-empty description="No objects detected" :image-size="80" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from "vue";
import type { Detection } from "@/types";

const COLORS = [
  "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7",
  "#DDA0DD", "#98D8C8", "#F7DC6F", "#BB8FCE", "#85C1E9",
];

const props = defineProps<{
  imageUrl: string;
  detections: Detection[];
}>();

const containerRef = ref<HTMLElement>();
const canvasRef = ref<HTMLCanvasElement>();
const imgRef = ref<HTMLImageElement>();

function drawBoxes() {
  nextTick(() => {
    const img = imgRef.value;
    const canvas = canvasRef.value;
    if (!img || !canvas || !containerRef.value) return;

    const rect = containerRef.value.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = img.offsetHeight;
    canvas.style.width = rect.width + "px";
    canvas.style.height = img.offsetHeight + "px";

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const scaleX = img.offsetWidth / img.naturalWidth;
    const scaleY = img.offsetHeight / img.naturalHeight;

    props.detections.forEach((det, i) => {
      const color = COLORS[i % COLORS.length];
      const { x1, y1, x2, y2 } = det.bbox;
      const sx = x1 * scaleX;
      const sy = y1 * scaleY;
      const sw = (x2 - x1) * scaleX;
      const sh = (y2 - y1) * scaleY;

      ctx.strokeStyle = color;
      ctx.lineWidth = 2;
      ctx.strokeRect(sx, sy, sw, sh);

      const label = `${det.class_name} ${(det.confidence * 100).toFixed(0)}%`;
      ctx.fillStyle = color;
      const textW = ctx.measureText(label).width + 8;
      ctx.fillRect(sx, sy - 20, textW, 20);
      ctx.fillStyle = "#fff";
      ctx.font = "12px sans-serif";
      ctx.fillText(label, sx + 4, sy - 5);
    });
  });
}

watch(() => props.detections, drawBoxes);
</script>

<style scoped>
.overlay-container {
  position: relative;
  display: inline-block;
  max-width: 100%;
}

.base-image {
  display: block;
  max-width: 100%;
  border-radius: 8px;
}

.overlay-canvas {
  position: absolute;
  top: 0;
  left: 0;
  pointer-events: none;
}

.no-result {
  padding: 20px 0;
}
</style>
