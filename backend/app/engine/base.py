from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class AbstractCVEngine(ABC):
    """Abstract base class for all CV inference engines."""

    name: str = "base"
    version: str = "0.1.0"

    @abstractmethod
    def load(self) -> None:
        """Load the model into memory."""
        ...

    @abstractmethod
    def infer(self, image_path: str, **kwargs: Any) -> dict[str, Any]:
        """Run inference on an image. Returns structured result dict."""
        ...

    @abstractmethod
    def unload(self) -> None:
        """Unload the model from memory."""
        ...

    @property
    def is_loaded(self) -> bool:
        """Check if the model is currently loaded in memory."""
        raise NotImplementedError
