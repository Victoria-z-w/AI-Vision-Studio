import client from "./client";
import type { InferResponse, TaskResult } from "@/types";

export interface AsyncUploadResponse {
  task_id: string;
  status: string;
  status_url: string;
}

export async function uploadImage(
  file: File,
  model: string,
  confidenceThreshold?: number
): Promise<TaskResult> {
  const form = new FormData();
  form.append("file", file);
  form.append("model", model);
  form.append("mode", "sync");
  if (confidenceThreshold !== undefined) {
    form.append("confidence_threshold", String(confidenceThreshold));
  }
  const { data } = await client.post<TaskResult>("/upload", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function uploadImageAsync(
  file: File,
  model: string,
  confidenceThreshold?: number
): Promise<AsyncUploadResponse> {
  const form = new FormData();
  form.append("file", file);
  form.append("model", model);
  form.append("mode", "async");
  if (confidenceThreshold !== undefined) {
    form.append("confidence_threshold", String(confidenceThreshold));
  }
  const { data } = await client.post<AsyncUploadResponse>("/upload", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function inferImage(
  file: File,
  model: string,
  confidenceThreshold?: number
): Promise<InferResponse> {
  const form = new FormData();
  form.append("file", file);
  form.append("model", model);
  if (confidenceThreshold !== undefined) {
    form.append("confidence_threshold", String(confidenceThreshold));
  }
  const { data } = await client.post<InferResponse>("/infer", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}
