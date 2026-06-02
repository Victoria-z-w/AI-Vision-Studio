<template>
  <div class="rembg-compare">
    <div class="compare-mode">
      <el-segmented v-model="mode" :options="modes" />
    </div>

    <div v-if="mode === 'side-by-side'" class="side-by-side">
      <div class="panel">
        <h4>Original</h4>
        <img :src="originalUrl" alt="Original" />
      </div>
      <div class="panel">
        <h4>Background Removed</h4>
        <div class="checkerboard-bg">
          <img :src="resolvedForeground" alt="Foreground" />
        </div>
      </div>
    </div>

    <div v-else class="slider-compare">
      <div class="slider-container">
        <img :src="originalUrl" class="compare-bg" alt="Original" />
        <div class="compare-fg" :style="{ width: sliderPos + '%' }">
          <img :src="resolvedForeground" alt="Foreground" />
        </div>
        <div class="slider-handle" :style="{ left: sliderPos + '%' }" @mousedown="startSlide">
          <el-icon><DArrowRight /></el-icon>
          <el-icon><DArrowLeft /></el-icon>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";

const props = defineProps<{
  originalUrl: string;
  foregroundUrl: string;
  foregroundBase64?: string;
}>();

const resolvedForeground = computed(() => props.foregroundBase64 || props.foregroundUrl);

const mode = ref("side-by-side");
const modes = [
  { label: "Side by Side", value: "side-by-side" },
  { label: "Slider", value: "slider" },
];

const sliderPos = ref(50);
let dragging = false;

function startSlide() {
  dragging = true;
  const onMove = (e: MouseEvent) => {
    if (!dragging) return;
    const el = document.querySelector(".slider-container") as HTMLElement;
    if (!el) return;
    const rect = el.getBoundingClientRect();
    sliderPos.value = Math.max(0, Math.min(100, ((e.clientX - rect.left) / rect.width) * 100));
  };
  const onUp = () => {
    dragging = false;
    document.removeEventListener("mousemove", onMove);
    document.removeEventListener("mouseup", onUp);
  };
  document.addEventListener("mousemove", onMove);
  document.addEventListener("mouseup", onUp);
}
</script>

<style scoped>
.compare-mode {
  margin-bottom: 16px;
  display: flex;
  justify-content: center;
}

.side-by-side {
  display: flex;
  gap: 24px;
}

.panel {
  flex: 1;
  text-align: center;
}

.panel h4 {
  margin: 0 0 8px;
  font-size: 14px;
  color: #606266;
}

.panel img {
  max-width: 100%;
  max-height: 500px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.checkerboard-bg {
  display: inline-block;
  background-image: linear-gradient(45deg, #eee 25%, transparent 25%),
    linear-gradient(-45deg, #eee 25%, transparent 25%),
    linear-gradient(45deg, transparent 75%, #eee 75%),
    linear-gradient(-45deg, transparent 75%, #eee 75%);
  background-size: 20px 20px;
  background-position: 0 0, 0 10px, 10px -10px, -10px 0px;
  border-radius: 8px;
}

.slider-compare {
  display: flex;
  justify-content: center;
}

.slider-container {
  position: relative;
  display: inline-block;
  max-width: 100%;
}

.compare-bg,
.compare-fg img {
  max-width: 100%;
  max-height: 500px;
  border-radius: 8px;
  display: block;
}

.compare-fg {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  overflow: hidden;
  border-radius: 8px 0 0 8px;
}

.slider-handle {
  position: absolute;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 40px;
  height: 40px;
  background: #fff;
  border: 2px solid #4ECDC4;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: ew-resize;
  color: #4ECDC4;
  z-index: 10;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}
</style>
