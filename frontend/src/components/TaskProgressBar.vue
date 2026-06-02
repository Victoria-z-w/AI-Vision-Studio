<template>
  <div v-if="visible" class="task-progress">
    <el-progress
      :percentage="progress"
      :status="progress === 100 ? 'success' : undefined"
      :stroke-width="8"
    />
    <p class="progress-text">{{ statusText }}</p>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{
  status: string;
  progress: number;
}>();

const visible = computed(() => props.status !== "idle" && props.status !== "SUCCESS");

const statusText = computed(() => {
  const texts: Record<string, string> = {
    PENDING: "Waiting in queue...",
    PROCESSING: `Processing... ${props.progress}%`,
    FAILED: "Inference failed",
    TIMEOUT: "Inference timed out",
  };
  return texts[props.status] || props.status;
});
</script>

<style scoped>
.task-progress {
  padding: 16px 0;
}

.progress-text {
  margin: 8px 0 0;
  font-size: 13px;
  color: #909399;
  text-align: center;
}
</style>
