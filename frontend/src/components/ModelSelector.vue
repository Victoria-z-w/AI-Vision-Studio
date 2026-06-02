<template>
  <div class="model-selector">
    <div
      v-for="m in models"
      :key="m.value"
      class="model-card"
      :class="{ active: modelValue === m.value }"
      @click="$emit('update:modelValue', m.value)"
    >
      <el-icon class="model-icon" :size="28">
        <component :is="m.icon" />
      </el-icon>
      <div class="model-info">
        <span class="model-name">{{ m.label }}</span>
        <span class="model-desc">{{ m.desc }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ModelType } from "@/types";

defineProps<{ modelValue: string }>();
defineEmits<{ (e: "update:modelValue", v: string): void }>();

const models = [
  { value: "yolo", label: "YOLOv8n", desc: "Object Detection", icon: "Aim" },
  { value: "rembg", label: "rembg", desc: "Background Removal", icon: "PictureFilled" },
  { value: "ocr", label: "PaddleOCR", desc: "Text Recognition", icon: "Document" },
] as const;
</script>

<style scoped>
.model-selector {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.model-card {
  flex: 1;
  min-width: 160px;
  padding: 20px 16px;
  border: 2px solid #e4e7ed;
  border-radius: 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 12px;
  transition: all 0.25s;
  background: #fff;
}

.model-card:hover {
  border-color: #4ECDC4;
  box-shadow: 0 4px 16px rgba(78, 205, 196, 0.15);
}

.model-card.active {
  border-color: #4ECDC4;
  background: #e8faf8;
}

.model-icon {
  color: #4ECDC4;
}

.model-info {
  display: flex;
  flex-direction: column;
}

.model-name {
  font-weight: 600;
  font-size: 15px;
  color: #303133;
}

.model-desc {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}
</style>
