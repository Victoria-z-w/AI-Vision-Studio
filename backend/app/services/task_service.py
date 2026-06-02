from __future__ import annotations

import logging
import time
import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.engine.registry import model_registry
from app.models.file import File
from app.models.task import Task, TaskStatus
from app.preprocessing.pipeline import compute_sha256_short, run_preprocessing
from app.storage.file_manager import file_manager
from app.utils.image import get_image_info, image_to_base64, numpy_to_native

logger = logging.getLogger(__name__)


def _make_json_safe(data: dict) -> dict:
    """Remove non-JSON-serializable objects and convert numpy types."""
    cleaned = {}
    for k, v in data.items():
        if hasattr(v, "save"):  # PIL Image
            continue
        cleaned[k] = numpy_to_native(v)
    return cleaned


async def create_task(
    db: AsyncSession,
    session_id: str,
    model_type: str,
    file_content: bytes,
    original_name: str,
    confidence_threshold: float | None = None,
) -> dict:
    """Create a task, run preprocessing + inference, return full result."""
    task_id = str(uuid.uuid4())
    start_time = time.perf_counter()

    # Save upload
    input_path = file_manager.save_upload(session_id, task_id, file_content, original_name)

    # Create task record
    task = Task(
        id=task_id,
        session_id=session_id,
        model_type=model_type,
        status=TaskStatus.PROCESSING.value,
        parameters={"confidence_threshold": confidence_threshold} if confidence_threshold else None,
    )
    db.add(task)
    await db.flush()

    # Preprocessing
    preproc_dir = file_manager.task_dir(session_id, task_id) / "preproc"
    preproc_path = run_preprocessing(input_path, preproc_dir)
    sha = compute_sha256_short(preproc_path)
    img_info = get_image_info(preproc_path)

    # Save input file record
    db.add(
        File(
            task_id=task_id,
            file_type="input",
            original_name=original_name,
            storage_path=str(input_path),
            mime_type=f"image/{img_info['format'].lower()}" if img_info["format"] else "image/png",
            size_bytes=len(file_content),
            width=img_info["width"],
            height=img_info["height"],
            sha256_short=sha,
        )
    )
    await db.flush()

    # Inference
    try:
        engine = model_registry.get_engine(model_type)
        infer_result = engine.infer(str(preproc_path), confidence_threshold=confidence_threshold)

        inference_time_ms = (time.perf_counter() - start_time) * 1000
        meta = {
            "inference_time_ms": round(inference_time_ms, 1),
            "device": model_registry.device,
            "model_version": getattr(engine, "version", "unknown"),
            "confidence_threshold": confidence_threshold
            or (
                settings.CONFIDENCE_THRESHOLD
                if model_type == "yolo"
                else settings.OCR_CONFIDENCE_THRESHOLD
            ),
        }

        result_data = _build_result(task_id, session_id, model_type, infer_result, meta)
        task.status = TaskStatus.SUCCESS.value
        task.result_json = numpy_to_native(result_data)
        task.inference_time_ms = inference_time_ms
        task.device = model_registry.device
        task.completed_at = datetime.now(UTC)

        return result_data

    except Exception as e:
        logger.exception(f"Inference failed for task {task_id}")
        task.status = TaskStatus.FAILED.value
        task.error_message = str(e)
        task.completed_at = datetime.now(UTC)
        raise


def _build_result(
    task_id: str,
    session_id: str,
    model_type: str,
    infer_result: dict,
    meta: dict,
) -> dict:
    """Build the structured result response, saving visualization files.

    Non-serializable objects (PIL Images) are extracted from infer_result
    and saved to disk BEFORE any JSON serialization occurs.
    """
    # ── Extract non-serializable data BEFORE save_json ──
    foreground_img = infer_result.pop("foreground", None) if model_type == "rembg" else None
    foreground_base64 = None

    if foreground_img is not None:
        file_manager.save_image(session_id, task_id, foreground_img, "foreground")
        foreground_base64 = image_to_base64(foreground_img)

    # Now infer_result is safe to serialize
    file_manager.save_json(session_id, task_id, infer_result)

    result = {
        "task_id": task_id,
        "model": model_type,
        "status": "SUCCESS",
        "result": _strip_model_specific(infer_result),
        "raw_result_url": f"/api/v1/tasks/{task_id}/result.json",
        "meta": meta,
        "created_at": datetime.now(UTC).isoformat(),
    }

    if model_type == "yolo":
        from app.services.visualization import draw_yolo_boxes

        vis_img = draw_yolo_boxes(
            file_manager.get_path(session_id, task_id, "preproc/preprocessed.png"),
            infer_result["detections"],
        )
        file_manager.save_image(session_id, task_id, vis_img, "visualization")
        result["visualization_url"] = f"/api/v1/tasks/{task_id}/visualization.png"

    elif model_type == "ocr":
        from app.services.visualization import draw_ocr_boxes

        vis_img = draw_ocr_boxes(
            file_manager.get_path(session_id, task_id, "preproc/preprocessed.png"),
            infer_result["regions"],
        )
        file_manager.save_image(session_id, task_id, vis_img, "visualization")
        result["visualization_url"] = f"/api/v1/tasks/{task_id}/visualization.png"

    elif model_type == "rembg":
        if foreground_base64:
            result["foreground_url"] = f"/api/v1/tasks/{task_id}/foreground.png"
            result["foreground_base64"] = foreground_base64
        result["result"]["image_size"] = infer_result.get("image_size", {})

    return result


def _strip_model_specific(infer_result: dict) -> dict:
    """Return a JSON-safe copy of the inference result."""
    return _make_json_safe(infer_result)


async def get_task(db: AsyncSession, task_id: str) -> Task | None:
    result = await db.execute(select(Task).where(Task.id == task_id))
    return result.scalar_one_or_none()


async def get_task_status(db: AsyncSession, task_id: str) -> dict | None:
    task = await get_task(db, task_id)
    if task is None:
        return None

    resp = {
        "task_id": task.id,
        "model": task.model_type,
        "status": task.status,
        "progress": task.progress,
        "meta": {
            "inference_time_ms": task.inference_time_ms,
            "device": task.device,
        } if task.inference_time_ms else None,
        "error_message": task.error_message,
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "started_at": task.started_at.isoformat() if task.started_at else None,
        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
    }

    if task.result_json:
        resp["result"] = task.result_json.get("result")
        resp["visualization_url"] = task.result_json.get("visualization_url")
        resp["foreground_url"] = task.result_json.get("foreground_url")
        resp["foreground_base64"] = task.result_json.get("foreground_base64")
        resp["raw_result_url"] = task.result_json.get("raw_result_url")

    return resp


async def list_tasks(
    db: AsyncSession,
    session_id: str,
    model: str | None = None,
    status: str | None = None,
    q: str | None = None,
    page: int = 1,
    size: int = 20,
) -> dict:
    query = select(Task).where(Task.session_id == session_id)

    if model:
        query = query.where(Task.model_type == model)
    if status:
        query = query.where(Task.status == status)

    query = query.order_by(Task.created_at.desc())

    total_query = select(func.count()).select_from(Task).where(Task.session_id == session_id)
    if model:
        total_query = total_query.where(Task.model_type == model)
    if status:
        total_query = total_query.where(Task.status == status)

    total_result = await db.execute(total_query)
    total = total_result.scalar() or 0

    query = query.offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    tasks = result.scalars().all()

    items = []
    for t in tasks:
        items.append({
            "task_id": t.id,
            "model": t.model_type,
            "status": t.status,
            "thumbnail_url": f"/api/v1/tasks/{t.id}/thumbnail.jpg",
            "inference_time_ms": t.inference_time_ms,
            "created_at": t.created_at.isoformat() if t.created_at else "",
        })

    return {
        "items": items,
        "pagination": {
            "page": page,
            "size": size,
            "total": total,
            "has_next": (page * size) < total,
        },
    }


async def delete_task(db: AsyncSession, task_id: str, session_id: str) -> bool:
    task = await get_task(db, task_id)
    if task is None or task.session_id != session_id:
        return False
    file_manager.delete_task(session_id, task_id)
    await db.delete(task)
    return True
