from __future__ import annotations

from pydantic import BaseModel, Field


class TaskUploadRequest(BaseModel):
    model: str = Field(..., pattern=r"^(yolo|rembg|ocr)$")
    mode: str = Field(default="sync", pattern=r"^(sync|async)$")
    confidence_threshold: float | None = Field(default=None, ge=0.0, le=1.0)


class TaskSyncResponse(BaseModel):
    task_id: str
    model: str
    status: str
    result: dict | None = None
    visualization_url: str | None = None
    raw_result_url: str | None = None
    foreground_url: str | None = None
    meta: dict | None = None
    created_at: str


class TaskAsyncResponse(BaseModel):
    task_id: str
    status: str
    status_url: str


class TaskStatusResponse(BaseModel):
    task_id: str
    model: str
    status: str
    progress: int
    result: dict | None = None
    visualization_url: str | None = None
    foreground_url: str | None = None
    meta: dict | None = None
    error_message: str | None = None
    created_at: str | None = None
    started_at: str | None = None
    completed_at: str | None = None


class TaskHistoryItem(BaseModel):
    task_id: str
    model: str
    status: str
    thumbnail_url: str | None = None
    inference_time_ms: float | None = None
    created_at: str


class TaskHistoryResponse(BaseModel):
    items: list[TaskHistoryItem]
    pagination: dict


class TaskDeleteRequest(BaseModel):
    task_ids: list[str]


class ErrorResponse(BaseModel):
    error: str
    detail: str
