from __future__ import annotations

import hashlib
import logging
from pathlib import Path

from PIL import Image, ImageOps

from app.config import settings

logger = logging.getLogger(__name__)

SUPPORTED_FORMATS = {"JPEG", "PNG", "WebP", "BMP", "TIFF"}
SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".tif"}


def run_preprocessing(image_path: str | Path, output_dir: str | Path) -> Path:
    """Run the full preprocessing pipeline and return the preprocessed image path."""
    image_path = Path(image_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    img = Image.open(image_path)

    # EXIF orientation
    img = ImageOps.exif_transpose(img)

    # Colorspace normalization
    if img.mode == "CMYK":
        img = img.convert("RGB")
    elif img.mode == "RGBA":
        background = Image.new("RGB", img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[3])
        img = background
    elif img.mode == "P":
        img = img.convert("RGBA").convert("RGB")
    elif img.mode == "L":
        img = img.convert("RGB")
    elif img.mode == "1":
        img = img.convert("RGB")
    elif img.mode not in ("RGB",):
        img = img.convert("RGB")

    # Resize if too large
    max_dim = settings.MAX_IMAGE_DIMENSION
    w, h = img.size
    if max(w, h) > max_dim:
        ratio = max_dim / max(w, h)
        new_size = (int(w * ratio), int(h * ratio))
        img = img.resize(new_size, Image.LANCZOS)
        logger.info(f"Resized {w}x{h} -> {new_size[0]}x{new_size[1]} (max {max_dim}px)")

    # Save preprocessed (fixed name since output_dir is already task-specific)
    out_path = output_dir / "preprocessed.png"
    img.save(out_path, "PNG")
    return out_path


def compute_sha256_short(file_path: Path) -> str:
    """Compute first 12 hex digits of SHA-256 for image deduplication."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()[:12]
