from __future__ import annotations

from pydantic import BaseModel


class BBox(BaseModel):
    x1: int
    y1: int
    x2: int
    y2: int


class Detection(BaseModel):
    bbox: BBox
    class_id: int
    class_name: str
    confidence: float
    area_px: int
    center: dict[str, int]


class YOLOResult(BaseModel):
    detections: list[Detection]
    count: int
    image_size: dict[str, int]


class OCRRegion(BaseModel):
    bbox: list[list[int]]
    text: str
    confidence: float


class OCRResult(BaseModel):
    regions: list[OCRRegion]
    full_text: str
    region_count: int
    image_size: dict[str, int]


class RembgResult(BaseModel):
    foreground_url: str
    original_url: str
    image_size: dict[str, int]


class InferenceMeta(BaseModel):
    inference_time_ms: float
    device: str
    model_version: str
    confidence_threshold: float | None = None
