import { defineStore } from "pinia";
import { ref } from "vue";

export type UploadStatus = "idle" | "uploading" | "processing" | "done" | "error";

export const useUploadStore = defineStore("upload", () => {
  const status = ref<UploadStatus>("idle");
  const progress = ref(0);
  const errorMessage = ref("");
  const selectedModel = ref<string>("yolo");
  const confidenceThreshold = ref<number>(0.25);
  const file = ref<File | null>(null);
  const previewUrl = ref<string>("");

  function setFile(f: File) {
    file.value = f;
    previewUrl.value = URL.createObjectURL(f);
  }

  function setModel(model: string) {
    selectedModel.value = model;
    if (model === "yolo") confidenceThreshold.value = 0.25;
    else if (model === "ocr") confidenceThreshold.value = 0.5;
  }

  function reset() {
    status.value = "idle";
    progress.value = 0;
    errorMessage.value = "";
    if (previewUrl.value) URL.revokeObjectURL(previewUrl.value);
    file.value = null;
    previewUrl.value = "";
  }

  return {
    status,
    progress,
    errorMessage,
    selectedModel,
    confidenceThreshold,
    file,
    previewUrl,
    setFile,
    setModel,
    reset,
  };
});
