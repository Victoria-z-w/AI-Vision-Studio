<template>
  <div class="upload-widget">
    <el-upload
      ref="uploadRef"
      class="upload-area"
      drag
      :auto-upload="false"
      :limit="1"
      :on-change="handleChange"
      :on-remove="handleRemove"
      :accept="'.jpg,.jpeg,.png,.webp,.bmp,.tiff'"
      :file-list="fileList"
    >
      <el-icon class="upload-icon"><UploadFilled /></el-icon>
      <div class="upload-text">
        <p class="upload-hint">Drag & drop an image here, or click to browse</p>
        <p class="upload-sub">JPEG / PNG / WebP / BMP / TIFF, max 20 MB</p>
      </div>
    </el-upload>
    <div v-if="previewUrl" class="preview-area">
      <img :src="previewUrl" alt="Preview" class="preview-image" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import type { UploadFile, UploadInstance } from "element-plus";
import { useUploadStore } from "@/stores/upload";

const store = useUploadStore();
const uploadRef = ref<UploadInstance>();
const fileList = ref<UploadFile[]>([]);
const previewUrl = ref<string>("");

const emit = defineEmits<{
  (e: "file-change", file: File | null): void;
}>();

function handleChange(file: UploadFile) {
  if (file.raw) {
    store.setFile(file.raw);
    previewUrl.value = URL.createObjectURL(file.raw);
    emit("file-change", file.raw);
  }
}

function handleRemove() {
  store.reset();
  previewUrl.value = "";
  emit("file-change", null);
}

watch(
  () => store.file,
  (f) => {
    if (!f) previewUrl.value = "";
  }
);
</script>

<style scoped>
.upload-widget {
  width: 100%;
}

.upload-area {
  width: 100%;
}

:deep(.el-upload-dragger) {
  padding: 40px 20px;
  border: 2px dashed #c0c4cc;
  border-radius: 8px;
  transition: border-color 0.3s;
}

:deep(.el-upload-dragger:hover) {
  border-color: #4ECDC4;
}

.upload-icon {
  font-size: 48px;
  color: #c0c4cc;
}

.upload-text {
  margin-top: 12px;
}

.upload-hint {
  font-size: 15px;
  color: #606266;
  margin: 0;
}

.upload-sub {
  font-size: 12px;
  color: #909399;
  margin: 6px 0 0;
}

.preview-area {
  margin-top: 16px;
  text-align: center;
}

.preview-image {
  max-width: 100%;
  max-height: 320px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}
</style>
