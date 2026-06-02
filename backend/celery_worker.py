from __future__ import annotations

import asyncio
import logging
import time
from datetime import datetime, timezone

from celery import Celery
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.engine.registry import model_registry
from app.models import async_session
from app.models.file import File
from app.models.task import Task, TaskStatus
from app.preprocessing.pipeline import compute_sha256_short, run_preprocessing
from app.services.task_service import _build_result
from app.storage.file_manager import file_manager
from app.utils.image import get_image_info, numpy_to_native

logger = logging.getLogger(__name__)

celery_app = Celery(
    "ai_vision_studio",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    task_track_started=True,
    task_soft_time_limit=settings.INFERENCE_TIMEOUT_S,
)


@celery_app.task(name="inference.run", bind=True, max_retries=0)
def run_inference_task(self, task_id: str, session_id: str, model_type: str, input_path: str):
    """Celery task: run CV inference asynchronously."""
    start_time = time.perf_counter()

    async def _run():
        async with async_session() as db:
            result = await db.execute(select(Task).where(Task.id == task_id))
            task = result.scalar_one_or_none()
            if task is None:
                return

            task.status = TaskStatus.PROCESSING.value
            task.started_at = datetime.now(timezone.utc)
            await db.flush()

            try:
                # Preprocessing
                preproc_dir = file_manager.task_dir(session_id, task_id) / "preproc"
                preproc_path = run_preprocessing(input_path, preproc_dir)
                sha = compute_sha256_short(preproc_path)
                img_info = get_image_info(preproc_path)

                # Create input file record
                db.add(
                    File(
                        task_id=task_id,
                        file_type="input",
                        original_name="image.png",
                        storage_path=str(input_path),
                        mime_type=f"image/{img_info['format'].lower()}" if img_info["format"] else "image/png",
                        size_bytes=preproc_path.stat().st_size,
                        width=img_info["width"],
                        height=img_info["height"],
                        sha256_short=sha,
                    )
                )
                await db.flush()

                # Inference
                threshold = task.parameters.get("confidence_threshold") if task.parameters else None
                engine = model_registry.get_engine(model_type)
                infer_result = engine.infer(str(preproc_path), confidence_threshold=threshold)

                inference_time_ms = (time.perf_counter() - start_time) * 1000
                meta = {
                    "inference_time_ms": round(inference_time_ms, 1),
                    "device": model_registry.device,
                    "model_version": getattr(engine, "version", "unknown"),
                    "confidence_threshold": threshold,
                }

                result_data = _build_result(task_id, session_id, model_type, infer_result, meta)
                task.status = TaskStatus.SUCCESS.value
                task.result_json = numpy_to_native(result_data)
                task.inference_time_ms = inference_time_ms
                task.device = model_registry.device
                task.completed_at = datetime.now(timezone.utc)

            except Exception as e:
                logger.exception(f"Async inference failed for task {task_id}")
                task.status = TaskStatus.FAILED.value
                task.error_message = str(e)
                task.completed_at = datetime.now(timezone.utc)

    asyncio.run(_run())
