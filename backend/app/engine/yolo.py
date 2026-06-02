from __future__ import annotations

import logging
import time
from typing import Any

from app.config import settings
from app.engine.base import AbstractCVEngine

logger = logging.getLogger(__name__)

COCO_CLASSES = {
    0: "person", 1: "bicycle", 2: "car", 3: "motorcycle", 4: "airplane", 5: "bus",
    6: "train", 7: "truck", 8: "boat", 9: "traffic light", 10: "fire hydrant",
    11: "stop sign", 12: "parking meter", 13: "bench", 14: "bird", 15: "cat",
    16: "dog", 17: "horse", 18: "sheep", 19: "cow", 20: "elephant", 21: "bear",
    22: "zebra", 23: "giraffe", 24: "backpack", 25: "umbrella", 26: "handbag",
    27: "tie", 28: "suitcase", 29: "frisbee", 30: "skis", 31: "snowboard",
    32: "sports ball", 33: "kite", 34: "baseball bat", 35: "baseball glove",
    36: "skateboard", 37: "surfboard", 38: "tennis racket", 39: "bottle",
    40: "wine glass", 41: "cup", 42: "fork", 43: "knife", 44: "spoon", 45: "bowl",
    46: "banana", 47: "apple", 48: "sandwich", 49: "orange", 50: "broccoli",
    51: "carrot", 52: "hot dog", 53: "pizza", 54: "donut", 55: "cake",
    56: "chair", 57: "couch", 58: "potted plant", 59: "bed", 60: "dining table",
    61: "toilet", 62: "tv", 63: "laptop", 64: "mouse", 65: "remote", 66: "keyboard",
    67: "cell phone", 68: "microwave", 69: "oven", 70: "toaster", 71: "sink",
    72: "refrigerator", 73: "book", 74: "clock", 75: "vase", 76: "scissors",
    77: "teddy bear", 78: "hair drier", 79: "toothbrush",
}


def _create_yolo_engine(device: str) -> "YOLOEngine":
    return YOLOEngine(device)


class YOLOEngine(AbstractCVEngine):
    name = "yolov8n"
    version = "yolov8n.pt"

    def __init__(self, device: str = "cpu") -> None:
        self._device = device
        self._model = None

    def load(self) -> None:
        from ultralytics import YOLO

        self._model = YOLO("yolov8n.pt")

    def infer(
        self, image_path: str, confidence_threshold: float | None = None, **kwargs: Any
    ) -> dict[str, Any]:
        if self._model is None:
            self.load()

        conf = confidence_threshold or settings.CONFIDENCE_THRESHOLD
        start = time.perf_counter()

        results = self._model(image_path, device=self._device, verbose=False)
        elapsed_ms = (time.perf_counter() - start) * 1000

        detections = []
        if results and results[0].boxes:
            boxes = results[0].boxes
            for i in range(len(boxes.xyxy)):
                c = float(boxes.conf[i])
                if c < conf:
                    continue
                cls_id = int(boxes.cls[i])
                x1, y1, x2, y2 = boxes.xyxy[i].tolist()
                detections.append(
                    {
                        "bbox": {"x1": round(x1), "y1": round(y1), "x2": round(x2), "y2": round(y2)},
                        "class_id": cls_id,
                        "class_name": COCO_CLASSES.get(cls_id, f"class_{cls_id}"),
                        "confidence": round(c, 4),
                        "area_px": round((x2 - x1) * (y2 - y1)),
                        "center": {"x": round((x1 + x2) / 2), "y": round((y1 + y2) / 2)},
                    }
                )

        h, w = results[0].orig_shape if results else (0, 0)

        return {
            "detections": detections,
            "count": len(detections),
            "image_size": {"width": w, "height": h},
        }

    def unload(self) -> None:
        del self._model
        self._model = None

    @property
    def is_loaded(self) -> bool:
        return self._model is not None
