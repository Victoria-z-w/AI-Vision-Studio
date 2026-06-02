<template>
  <div class="ocr-overlay">
    <div class="overlay-container" ref="containerRef">
      <img :src="imageUrl" ref="imgRef" class="base-image" @load="draw" alt="OCR result" />
      <canvas ref="canvasRef" class="overlay-canvas" />
    </div>
    <div v-if="regions.length > 0" class="text-results">
      <div v-for="(r, i) in regions" :key="i" class="text-line">
        <span class="text-index" :style="{ background: COLORS[i % COLORS.length] }">{{ i + 1 }}</span>
        <span class="text-content">{{ r.text }}</span>
        <span class="text-conf">{{ (r.confidence * 100).toFixed(1) }}%</span>
      </div>
    </div>
    <div v-else class="no-result">
      <el-empty description="No text detected" :image-size="80" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from "vue";
import type { OCRRegion } from "@/types";

const COLORS = [
  "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7",
  "#DDA0DD", "#98D8C8", "#F7DC6F", "#BB8FCE", "#85C1E9",
];

const props = defineProps<{
  imageUrl: string;
  regions: OCRRegion[];
}>();

const containerRef = ref<HTMLElement>();
const canvasRef = ref<HTMLCanvasElement>();
const imgRef = ref<HTMLImageElement>();

function draw() {
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

    props.regions.forEach((region, i) => {
      const color = COLORS[i % COLORS.length];
      const pts = region.bbox;

      ctx.beginPath();
      ctx.moveTo(pts[0][0] * scaleX, pts[0][1] * scaleY);
      for (let j = 1; j < pts.length; j++) {
        ctx.lineTo(pts[j][0] * scaleX, pts[j][1] * scaleY);
      }
      ctx.closePath();
      ctx.strokeStyle = color;
      ctx.lineWidth = 2;
      ctx.stroke();
      ctx.fillStyle = color + "20";
      ctx.fill();

      // Draw index label
      const [x, y] = pts[0];
      ctx.fillStyle = color;
      ctx.fillRect(x * scaleX, y * scaleY - 18, 20, 18);
      ctx.fillStyle = "#fff";
      ctx.font = "11px sans-serif";
      ctx.fillText(String(i + 1), x * scaleX + 4, y * scaleY - 4);
    });
  });
}

watch(() => props.regions, draw);
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

.text-results {
  margin-top: 16px;
}

.text-line {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 0;
  border-bottom: 1px solid #f0f0f0;
}

.text-index {
  width: 22px;
  height: 22px;
  border-radius: 4px;
  color: #fff;
  font-size: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.text-content {
  flex: 1;
  font-size: 14px;
  color: #303133;
}

.text-conf {
  font-size: 12px;
  color: #909399;
}

.no-result {
  padding: 20px 0;
}
</style>
