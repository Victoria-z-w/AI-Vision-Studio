from __future__ import annotations

import logging
import time
from typing import Any

import numpy as np
from PIL import Image

from app.engine.base import AbstractCVEngine

logger = logging.getLogger(__name__)


def _create_rembg_engine(device: str) -> "RembgEngine":
    return RembgEngine(device)


class RembgEngine(AbstractCVEngine):
    name = "rembg"
    version = "2.0"

    def __init__(self, device: str = "cpu") -> None:
        self._device = device
        self._session = None

    def load(self) -> None:
        from rembg import new_session

        providers = (
            ["CUDAExecutionProvider", "CPUExecutionProvider"]
            if self._device == "cuda"
            else ["CPUExecutionProvider"]
        )
        self._session = new_session(providers=providers)

    def infer(self, image_path: str, **kwargs: Any) -> dict[str, Any]:
        if self._session is None:
            self.load()

        from rembg import remove

        start = time.perf_counter()
        input_image = Image.open(image_path).convert("RGB")
        output = remove(input_image, session=self._session)
        elapsed_ms = (time.perf_counter() - start) * 1000

        return {
            "foreground": output,
            "image_size": {"width": input_image.width, "height": input_image.height},
        }

    def unload(self) -> None:
        del self._session
        self._session = None

    @property
    def is_loaded(self) -> bool:
        return self._session is not None
