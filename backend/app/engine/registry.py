from __future__ import annotations

import logging
import time
from typing import Any

import torch

from app.config import settings

logger = logging.getLogger(__name__)


class ModelRegistry:
    """Central registry for CV model loading, caching, and inference dispatch."""

    def __init__(self) -> None:
        self._engines: dict[str, Any] = {}
        self._available: dict[str, bool] = {}
        self._device = self._resolve_device()

    def _resolve_device(self) -> str:
        if settings.DEVICE != "auto":
            return settings.DEVICE
        return "cuda" if torch.cuda.is_available() else "cpu"

    @property
    def device(self) -> str:
        return self._device

    def get_device_name(self) -> str:
        if self._device == "cuda":
            return f"cuda:0 ({torch.cuda.get_device_name(0)})"
        return "cpu"

    def set_availability(self, available: dict[str, bool]) -> None:
        """Update which models are available based on dependency checks."""
        self._available = available

    def is_available(self, name: str) -> bool:
        """Check whether a model's dependencies are installed."""
        if name not in self._engines:
            return False
        return self._available.get(name, True)

    def register(self, name: str, engine_factory: callable) -> None:
        self._engines[name] = {"factory": engine_factory, "instance": None, "loaded": False}

    def get_engine(self, name: str):
        if name not in self._engines:
            raise ValueError(f"Unknown model: {name}. Available: {list(self._engines.keys())}")
        if not self.is_available(name):
            raise ImportError(
                f"Model '{name}' is not available. Its dependencies are not installed."
            )
        entry = self._engines[name]
        if not entry["loaded"]:
            logger.info(f"Loading model '{name}' on {self._device}...")
            start = time.time()
            entry["instance"] = entry["factory"](self._device)
            entry["instance"].load()
            entry["loaded"] = True
            logger.info(f"Model '{name}' loaded in {time.time() - start:.1f}s")
        return entry["instance"]

    def is_loaded(self, name: str) -> bool:
        return self._engines.get(name, {}).get("loaded", False)

    def unload(self, name: str) -> None:
        if name in self._engines and self._engines[name]["loaded"]:
            self._engines[name]["instance"].unload()
            self._engines[name]["loaded"] = False
            self._engines[name]["instance"] = None
            logger.info(f"Model '{name}' unloaded")

    def get_status(self) -> list[dict]:
        return [
            {
                "name": name,
                "loaded": entry["loaded"],
                "device": self._device if entry["loaded"] else None,
            }
            for name, entry in self._engines.items()
        ]


model_registry = ModelRegistry()
