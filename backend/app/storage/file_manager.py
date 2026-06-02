from __future__ import annotations

import shutil
import uuid
from io import BytesIO
from pathlib import Path

from PIL import Image

from app.config import settings


class FileManager:
    """Manages file storage for uploads, preprocessed images, and results."""

    def __init__(self, base_dir: str | Path | None = None) -> None:
        self.base_dir = Path(base_dir or settings.UPLOAD_DIR)

    def session_dir(self, session_id: str) -> Path:
        return self.base_dir / session_id

    def task_dir(self, session_id: str, task_id: str) -> Path:
        d = self.session_dir(session_id) / task_id
        d.mkdir(parents=True, exist_ok=True)
        return d

    def save_upload(self, session_id: str, task_id: str, content: bytes, original_name: str) -> Path:
        d = self.task_dir(session_id, task_id)
        ext = Path(original_name).suffix or ".png"
        path = d / f"input_{uuid.uuid4().hex[:8]}{ext}"
        path.write_bytes(content)
        return path

    def save_image(self, session_id: str, task_id: str, image: Image.Image, name: str) -> Path:
        d = self.task_dir(session_id, task_id)
        path = d / f"{name}.png"
        image.save(path, "PNG")
        return path

    def save_bytes(self, session_id: str, task_id: str, data: BytesIO, name: str) -> Path:
        d = self.task_dir(session_id, task_id)
        path = d / name
        path.write_bytes(data.getvalue())
        return path

    def save_json(self, session_id: str, task_id: str, data: dict, name: str = "result") -> Path:
        import json

        from app.utils.image import numpy_to_native

        d = self.task_dir(session_id, task_id)
        path = d / f"{name}.json"
        path.write_text(json.dumps(numpy_to_native(data), indent=2, ensure_ascii=False))
        return path

    def get_path(self, session_id: str, task_id: str, filename: str) -> Path:
        return self.task_dir(session_id, task_id) / filename

    def delete_task(self, session_id: str, task_id: str) -> None:
        d = self.task_dir(session_id, task_id)
        if d.exists():
            shutil.rmtree(d)

    def cleanup_session(self, session_id: str) -> None:
        d = self.session_dir(session_id)
        if d.exists():
            shutil.rmtree(d)

    def relative_path(self, full_path: Path) -> str:
        """Return path relative to base_dir."""
        try:
            return str(full_path.relative_to(self.base_dir))
        except ValueError:
            return str(full_path)


file_manager = FileManager()
