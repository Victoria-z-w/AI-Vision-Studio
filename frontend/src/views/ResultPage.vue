<template>
  <div class="result-page" :class="{ inline }">
    <div v-if="loading" class="loading-section">
      <el-skeleton :rows="8" animated />
    </div>

    <TaskProgressBar
      v-if="polling && task"
      :status="task.status"
      :progress="task.meta ? 100 : 30"
    />

    <template v-else-if="task">
      <el-card class="result-card">
        <template #header>
          <div class="card-header">
            <span class="task-title">
              Inference Result
              <el-tag :type="statusTagType" size="small" class="ml-2">{{ task.status }}</el-tag>
            </span>
            <div class="header-actions">
              <el-tag size="small">{{ task.model }}</el-tag>
              <span v-if="task.meta?.inference_time_ms" class="time-info">
                {{ (task.meta.inference_time_ms / 1000).toFixed(2) }}s
              </span>
            </div>
          </div>
        </template>

        <!-- Visualization -->
        <div v-if="task.visualization_url || task.foreground_url || task.foreground_base64" class="vis-section">
          <VisualizationViewer
            :task-id="task.task_id"
            :model="task.model"
            :result="task.result as Record<string, unknown>"
            :foreground-base64="task.foreground_base64"
          />
        </div>

        <!-- Metadata -->
        <el-descriptions v-if="task.meta" :column="3" border class="meta-table">
          <el-descriptions-item label="Model">{{ task.model }}</el-descriptions-item>
          <el-descriptions-item label="Device">{{ task.meta.device }}</el-descriptions-item>
          <el-descriptions-item label="Time">
            {{ (task.meta.inference_time_ms / 1000).toFixed(2) }}s
          </el-descriptions-item>
          <el-descriptions-item label="Version">{{ task.meta.model_version }}</el-descriptions-item>
          <el-descriptions-item v-if="task.meta.confidence_threshold" label="Confidence">
            {{ task.meta.confidence_threshold }}
          </el-descriptions-item>
        </el-descriptions>

        <!-- JSON Result -->
        <div v-if="task.result" class="json-section">
          <JsonViewer :data="task.result" />
        </div>

        <!-- Downloads -->
        <div class="actions">
          <el-button
            v-if="task.visualization_url"
            type="primary"
            @click="downloadFile(task.visualization_url)"
          >
            <el-icon><Download /></el-icon> Visualization
          </el-button>
          <el-button
            v-if="task.foreground_url"
            type="success"
            @click="downloadFile(task.foreground_url)"
          >
            <el-icon><Download /></el-icon> Foreground PNG
          </el-button>
          <el-button
            v-if="task.foreground_base64"
            type="success"
            @click="downloadBase64Image(task.foreground_base64, 'foreground.png')"
          >
            <el-icon><Download /></el-icon> Foreground PNG (Base64)
          </el-button>
          <el-button
            v-if="task.raw_result_url"
            type="info"
            @click="downloadFile(task.raw_result_url)"
          >
            <el-icon><Download /></el-icon> Result JSON
          </el-button>
        </div>
      </el-card>
    </template>

    <el-empty v-else description="Result not found" :image-size="80" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from "vue";
import { useRoute } from "vue-router";
import { getTaskStatus } from "@/api/tasks";
import type { TaskResult } from "@/types";
import VisualizationViewer from "@/components/VisualizationViewer.vue";
import JsonViewer from "@/components/JsonViewer.vue";
import TaskProgressBar from "@/components/TaskProgressBar.vue";
import { useBase64 } from "@/composables/useBase64";

const { downloadBase64: downloadBase64Image } = useBase64();

const props = defineProps<{
  taskId?: string;
  inline?: boolean;
}>();

const route = useRoute();
const task = ref<TaskResult | null>(null);
const loading = ref(true);
const polling = ref(false);
let _pollTimer: ReturnType<typeof setInterval> | null = null;

const currentTaskId = computed(() => props.taskId || (route.params.taskId as string));

const statusTagType = computed(() => {
  const s = task.value?.status;
  if (s === "SUCCESS") return "success";
  if (s === "FAILED" || s === "TIMEOUT") return "danger";
  return "warning";
});

const isPolling = computed(() => {
  const s = task.value?.status;
  return s === "PENDING" || s === "PROCESSING";
});

onMounted(async () => {
  if (currentTaskId.value) {
    await loadTask();
  }
});

watch(currentTaskId, async () => {
  stopPolling();
  if (currentTaskId.value) await loadTask();
});

watch(isPolling, (val) => {
  if (val) startPolling();
});

onUnmounted(() => stopPolling());

async function loadTask() {
  loading.value = true;
  try {
    task.value = await getTaskStatus(currentTaskId.value);
  } catch {
    task.value = null;
  } finally {
    loading.value = false;
  }
}

function startPolling() {
  if (_pollTimer) return;
  polling.value = true;
  _pollTimer = setInterval(async () => {
    try {
      const result = await getTaskStatus(currentTaskId.value);
      task.value = result;
      if (result.status === "SUCCESS" || result.status === "FAILED" || result.status === "TIMEOUT") {
        stopPolling();
      }
    } catch {
      stopPolling();
    }
  }, 1500);
}

function stopPolling() {
  if (_pollTimer) {
    clearInterval(_pollTimer);
    _pollTimer = null;
  }
  polling.value = false;
}

function downloadFile(url: string) {
  window.open(url, "_blank");
}
</script>

<style scoped>
.result-page {
  max-width: 900px;
  margin: 0 auto;
}

.result-page.inline {
  max-width: 100%;
}

.loading-section {
  padding: 40px;
}

.result-card {
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.task-title {
  font-size: 16px;
  font-weight: 600;
}

.ml-2 {
  margin-left: 8px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.time-info {
  font-size: 13px;
  color: #909399;
}

.vis-section {
  margin-bottom: 24px;
}

.meta-table {
  margin-bottom: 24px;
}

.json-section {
  margin-bottom: 24px;
}

.actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
</style>
