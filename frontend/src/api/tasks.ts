import client from "./client";
import type { TaskResult, TaskHistoryResponse } from "@/types";

export async function getTaskStatus(taskId: string): Promise<TaskResult> {
  const { data } = await client.get<TaskResult>(`/tasks/${taskId}/status`);
  return data;
}

export async function getTaskHistory(params: {
  model?: string;
  status?: string;
  q?: string;
  page?: number;
  size?: number;
}): Promise<TaskHistoryResponse> {
  const { data } = await client.get<TaskHistoryResponse>("/tasks", { params });
  return data;
}

export async function deleteTask(taskId: string): Promise<void> {
  await client.delete(`/tasks/${taskId}`);
}

export async function deleteTasksBatch(taskIds: string[]): Promise<void> {
  await client.delete("/tasks/batch", { data: { task_ids: taskIds } });
}

export function getVisualizationUrl(taskId: string): string {
  return `/api/v1/tasks/${taskId}/visualization.png`;
}

export function getForegroundUrl(taskId: string): string {
  return `/api/v1/tasks/${taskId}/foreground.png`;
}

export function getThumbnailUrl(taskId: string): string {
  return `/api/v1/tasks/${taskId}/thumbnail.jpg`;
}
