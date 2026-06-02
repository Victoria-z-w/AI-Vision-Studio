<template>
  <div class="upload-page">
    <el-card class="upload-card">
      <h2>Upload Image</h2>
      <UploadWidget @file-change="onFileChange" />

      <div v-if="hasFile" class="config-section">
        <h3>Select Model</h3>
        <ModelSelector v-model="store.selectedModel" />

        <div class="mode-toggle">
          <span class="mode-label">Execution Mode:</span>
          <el-radio-group v-model="asyncMode" size="small">
            <el-radio-button :value="false">Sync</el-radio-button>
            <el-radio-button :value="true">Async</el-radio-button>
          </el-radio-group>
        </div>

        <div v-if="store.selectedModel === 'yolo' || store.selectedModel === 'ocr'" class="confidence-slider">
          <span class="slider-label">
            Confidence Threshold: {{ store.confidenceThreshold.toFixed(2) }}
          </span>
          <el-slider
            v-model="store.confidenceThreshold"
            :min="0.01"
            :max="1"
            :step="0.01"
            show-input
          />
        </div>

        <el-button
          type="primary"
          size="large"
          class="run-btn"
          :loading="taskStore.isLoading"
          :disabled="!hasFile"
          @click="runInference"
        >
          <el-icon><VideoPlay /></el-icon>
          Run Inference ({{ store.selectedModel }})
        </el-button>

        <TaskProgressBar
          v-if="taskStore.isAsync"
          :status="taskStore.currentTask?.status || 'PENDING'"
          :progress="taskStore.progress"
        />
      </div>
    </el-card>

    <div v-if="taskStore.error" class="error-section">
      <el-alert :title="taskStore.error" type="error" show-icon closable @close="taskStore.clear()" />
    </div>

    <div v-if="taskStore.currentTask" class="result-section">
      <ResultPage :task-id="taskStore.currentTask.task_id" :inline="true" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { useRouter } from "vue-router";
import UploadWidget from "@/components/UploadWidget.vue";
import ModelSelector from "@/components/ModelSelector.vue";
import TaskProgressBar from "@/components/TaskProgressBar.vue";
import ResultPage from "@/views/ResultPage.vue";
import { useUploadStore } from "@/stores/upload";
import { useTaskStore } from "@/stores/task";

const router = useRouter();
const store = useUploadStore();
const taskStore = useTaskStore();
const asyncMode = ref(false);

const hasFile = computed(() => store.file !== null);

function onFileChange(file: File | null) {
  if (file) store.setModel(store.selectedModel);
}

async function runInference() {
  if (!store.file) return;
  try {
    if (asyncMode.value) {
      const taskId = await taskStore.runInferenceAsync(
        store.file,
        store.selectedModel,
        store.selectedModel === "yolo" || store.selectedModel === "ocr"
          ? store.confidenceThreshold
          : undefined
      );
      if (taskId) {
        router.push(`/tasks/${taskId}`);
      }
    } else {
      const result = await taskStore.runInference(
        store.file,
        store.selectedModel,
        store.selectedModel === "yolo" || store.selectedModel === "ocr"
          ? store.confidenceThreshold
          : undefined
      );
      if (result.task_id) {
        router.push(`/tasks/${result.task_id}`);
      }
    }
  } catch {
    // Error handled by store
  }
}
</script>

<style scoped>
.upload-page {
  max-width: 800px;
  margin: 0 auto;
}

.upload-card {
  margin-bottom: 24px;
}

.upload-card h2 {
  margin: 0 0 20px;
  font-size: 20px;
}

.config-section {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}

.config-section h3 {
  font-size: 16px;
  margin: 0 0 12px;
}

.mode-toggle {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 16px 0;
}

.mode-label {
  font-size: 14px;
  color: #606266;
}

.confidence-slider {
  margin: 20px 0;
}

.slider-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
  display: block;
}

.run-btn {
  width: 100%;
  margin-top: 16px;
  height: 48px;
  font-size: 16px;
}

.error-section {
  margin-bottom: 16px;
}

.result-section {
  margin-top: 24px;
}
</style>
