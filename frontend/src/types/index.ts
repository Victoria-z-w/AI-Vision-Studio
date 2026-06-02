// Detection types
export interface BBox {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

export interface Detection {
  bbox: BBox;
  class_id: number;
  class_name: string;
  confidence: number;
  area_px: number;
  center: { x: number; y: number };
}

export interface YOLOResult {
  detections: Detection[];
  count: number;
  image_size: { width: number; height: number };
}

// OCR types
export interface OCRRegion {
  bbox: number[][];
  text: string;
  confidence: number;
}

export interface OCRResult {
  regions: OCRRegion[];
  full_text: string;
  region_count: number;
  image_size: { width: number; height: number };
}

// Rembg types
export interface RembgResult {
  foreground_url: string;
  original_url: string;
  image_size: { width: number; height: number };
}

// Inference meta
export interface InferenceMeta {
  inference_time_ms: number;
  device: string;
  model_version: string;
  confidence_threshold?: number;
}

// Task
export interface TaskResult {
  task_id: string;
  model: string;
  status: string;
  result?: YOLOResult | OCRResult | Record<string, unknown>;
  visualization_url?: string;
  foreground_url?: string;
  foreground_base64?: string;
  raw_result_url?: string;
  meta?: InferenceMeta;
  created_at?: string;
}

export interface TaskHistoryItem {
  task_id: string;
  model: string;
  status: string;
  thumbnail_url?: string;
  inference_time_ms?: number;
  created_at: string;
}

export interface TaskHistoryResponse {
  items: TaskHistoryItem[];
  pagination: {
    page: number;
    size: number;
    total: number;
    has_next: boolean;
  };
}

export interface ModelStatus {
  name: string;
  loaded: boolean;
  device: string | null;
}

export type ModelType = "yolo" | "rembg" | "ocr";

// ── POST /api/v1/infer response types ──

export interface InferResponse {
  task_id: string;
  model: string;
  status: string;
  result: YOLOResult | OCRResult | Record<string, unknown>;
  vis_base64?: string;
  foreground_base64?: string;
  meta: InferenceMeta;
}
