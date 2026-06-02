from __future__ import annotations

import logging
import os
import time
from typing import Any

from app.config import settings
from app.engine.base import AbstractCVEngine

# Disable OneDNN / MKL-DNN before PaddlePaddle loads — avoids
# RuntimeError: (NotFound) OneDnnContext does not have the input Filter
os.environ["FLAGS_use_mkldnn"] = "0"

logger = logging.getLogger(__name__)


def _create_ocr_engine(device: str) -> "OCREngine":
    return OCREngine(device)


class OCREngine(AbstractCVEngine):
    name = "paddleocr"
    version = "2.8"

    def __init__(self, device: str = "cpu") -> None:
        self._device = device
        self._ocr = None

    def load(self) -> None:
        from paddleocr import PaddleOCR

        use_gpu = self._device == "cuda"
        self._ocr = PaddleOCR(
            use_angle_cls=True,
            lang="ch",
            use_gpu=use_gpu,
            show_log=False,
        )

    def infer(
        self, image_path: str, confidence_threshold: float | None = None, **kwargs: Any
    ) -> dict[str, Any]:
        if self._ocr is None:
            self.load()

        conf = confidence_threshold or settings.OCR_CONFIDENCE_THRESHOLD
        start = time.perf_counter()

        raw = self._ocr.ocr(image_path, cls=True)
        elapsed_ms = (time.perf_counter() - start) * 1000

        regions = []
        if raw and raw[0]:
            for line in raw[0]:
                bbox, (text, score) = line
                if score < conf:
                    continue
                bbox_int = [[int(pt[0]), int(pt[1])] for pt in bbox]
                regions.append(
                    {
                        "bbox": bbox_int,
                        "text": text,
                        "confidence": round(score, 4),
                    }
                )

        from PIL import Image
        img = Image.open(image_path)

        return {
            "regions": regions,
            "full_text": "\n".join(r["text"] for r in regions),
            "region_count": len(regions),
            "image_size": {"width": img.width, "height": img.height},
        }

    def unload(self) -> None:
        del self._ocr
        self._ocr = None

    @property
    def is_loaded(self) -> bool:
        return self._ocr is not None
