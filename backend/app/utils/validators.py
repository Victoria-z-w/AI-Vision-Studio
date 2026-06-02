from __future__ import annotations

from pathlib import Path

from fastapi import UploadFile

from app.config import settings

MAGIC_BYTES = {
    b"\xff\xd8\xff": "JPEG",
    b"\x89PNG\r\n\x1a\n": "PNG",
    b"RIFF": "WebP",
    b"BM": "BMP",
    b"MM\x00*": "TIFF",
    b"II*\x00": "TIFF",
}

SUPPORTED_MIMES = {"image/jpeg", "image/png", "image/webp", "image/bmp", "image/tiff"}


class ValidationError(Exception):
    """Raised when file validation fails."""

    def __init__(self, error_code: str, detail: str) -> None:
        self.error_code = error_code
        self.detail = detail


def validate_upload(file: UploadFile) -> tuple[bytes, str]:
    """Validate uploaded file and return (content_bytes, detected_format)."""
    # Check filename extension
    if file.filename:
        ext = Path(file.filename).suffix.lower()
    else:
        raise ValidationError("INVALID_FILENAME", "No filename provided")

    # Check content type
    if file.content_type and file.content_type not in SUPPORTED_MIMES:
        raise ValidationError(
            "UNSUPPORTED_FORMAT",
            f"Content-Type '{file.content_type}' is not supported. "
            f"Allowed: {', '.join(SUPPORTED_MIMES)}",
        )

    content = file.file.read()

    # Check size
    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise ValidationError(
            "FILE_TOO_LARGE",
            f"File size {len(content) / 1024 / 1024:.1f}MB exceeds limit of {settings.MAX_FILE_SIZE_MB}MB",
        )

    # Check magic bytes
    detected = _detect_format(content)
    if detected is None:
        raise ValidationError(
            "UNSUPPORTED_FORMAT",
            f"Cannot detect image format from file content. "
            f"Supported: JPEG, PNG, WebP, BMP, TIFF",
        )

    return content, detected


def _detect_format(content: bytes) -> str | None:
    for magic, fmt in MAGIC_BYTES.items():
        if content[: len(magic)] == magic:
            return fmt
    return None
