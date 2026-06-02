from __future__ import annotations

import base64
from io import BytesIO
from pathlib import Path

import numpy as np
from PIL import Image


def get_image_info(image_path: str | Path) -> dict:
    img = Image.open(image_path)
    return {
        "width": img.width,
        "height": img.height,
        "mode": img.mode,
        "format": img.format,
    }


def make_thumbnail(image_path: str | Path, size: tuple[int, int] = (300, 300)) -> BytesIO:
    """Create a thumbnail and return as BytesIO."""
    img = Image.open(image_path)
    img.thumbnail(size, Image.LANCZOS)
    buf = BytesIO()
    img.save(buf, "JPEG", quality=80)
    buf.seek(0)
    return buf


def image_to_bytes(img: Image.Image, fmt: str = "PNG") -> BytesIO:
    buf = BytesIO()
    img.save(buf, fmt)
    buf.seek(0)
    return buf


def image_to_base64(img: Image.Image, fmt: str = "PNG") -> str:
    """Convert a PIL Image to a base64-encoded data URI string."""
    buf = BytesIO()
    img.save(buf, fmt)
    buf.seek(0)
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    mime = "image/png" if fmt.upper() == "PNG" else f"image/{fmt.lower()}"
    return f"data:{mime};base64,{b64}"


def numpy_to_native(obj):
    """Recursively convert numpy types to native Python types for JSON serialization.

    PIL Images are silently dropped (returned as None) since they cannot be
    JSON-serialized — callers should extract them before serializing.
    """
    if hasattr(obj, "save") and hasattr(obj, "convert"):
        return None
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, dict):
        return {k: numpy_to_native(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [numpy_to_native(v) for v in obj]
    return obj


class NumpyJSONEncoder:
    """JSON encoder that handles numpy types and PIL Images.

    Usage: json.dumps(data, cls=NumpyJSONEncoder) — but since json.dumps
    doesn't support a custom cls override per-call in the same way as
    json.JSONEncoder, use numpy_to_native() before serialization instead.
    """

    @staticmethod
    def dumps(obj, **kwargs):
        return __import__("json").dumps(numpy_to_native(obj), **kwargs)
