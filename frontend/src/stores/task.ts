import { defineStore } from "pinia";
import { ref } from "vue";
import type { TaskResult } from "@/types";
import { uploadImage, uploadImageAsync } from "@/api/upload";
import { getTaskStatus } from "@/api/tasks";

export const useTaskStore = defineStore("task", () => {
  const currentTask = ref<TaskResult | null>(null);
  const isLoading = ref(false);
  const error = ref("");
  const isAsync = ref(false);
  const progress = ref(0);
  let _pollTimer: ReturnType<typeof setInterval> | null = null;

  async function runInference(f: File, model: string, confidenceThreshold?: number) {
    isLoading.value = true;
    error.value = "";
    try {
      const result = await uploadImage(f, model, confidenceThreshold);
      currentTask.value = result;
      return result;
    } catch (e: any) {
      const detail = e.response?.data?.detail || e.message || "";
      error.value = detail.includes("not JSON serializable")
        ? "Model inference failed — please try again"
        : detail || "Inference failed";
      throw e;
    } finally {
      isLoading.value = false;
    }
  }

  async function runInferenceAsync(f: File, model: string, confidenceThreshold?: number) {
    isLoading.value = true;
    error.value = "";
    isAsync.value = true;
    progress.value = 0;
    try {
      const { task_id } = await uploadImageAsync(f, model, confidenceThreshold);
      currentTask.value = { task_id, model, status: "PENDING" } as TaskResult;
      startPolling(task_id);
      return task_id;
    } catch (e: any) {
      const detail = e.response?.data?.detail || e.message || "";
      error.value = detail.includes("not JSON serializable")
        ? "Model inference failed — please try again"
        : detail || "Inference failed";
      throw e;
    } finally {
      isLoading.value = false;
    }
  }

  function startPolling(taskId: string) {
    stopPolling();
    _pollTimer = setInterval(async () => {
      try {
        const result = await getTaskStatus(taskId);
        currentTask.value = result;
        progress.value = result.meta ? 100 : 30;
        if (result.status === "SUCCESS" || result.status === "FAILED" || result.status === "TIMEOUT") {
          stopPolling();
          isAsync.value = false;
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
  }

  async function pollTask(taskId: string) {
    const result = await getTaskStatus(taskId);
    currentTask.value = result;
    return result;
  }

  function clear() {
    stopPolling();
    currentTask.value = null;
    error.value = "";
    isLoading.value = false;
    isAsync.value = false;
    progress.value = 0;
  }

  return {
    currentTask,
    isLoading,
    error,
    isAsync,
    progress,
    runInference,
    runInferenceAsync,
    pollTask,
    clear,
  };
});
