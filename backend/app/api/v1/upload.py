from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, Form, Request, Response, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_install_command, get_model_description
from app.engine.registry import model_registry
from app.models import get_db
from app.models.task import Task, TaskStatus
from app.schemas.task import ErrorResponse
from app.services.task_service import create_task
from app.storage.file_manager import file_manager
from app.utils.validators import ValidationError, validate_upload

from app.limiter import limiter

logger = logging.getLogger(__name__)

router = APIRouter()


def _get_session_id(request: Request, response: Response) -> str:
    sid = request.cookies.get("session_id")
    if not sid:
        sid = str(uuid.uuid4())
        response.set_cookie(
            key="session_id",
            value=sid,
            max_age=86400 * 30,
            httponly=True,
            samesite="lax",
        )
    return sid


def _model_missing_response(model: str) -> Response:
    """Build a structured 503 response for a model whose dependencies are not installed."""
    cmd = get_install_command(model) or f"pip install {model}"
    desc = get_model_description(model)
    return Response(
        content=(
            '{"error":"MODEL_UNAVAILABLE",'
            f'"message":"{model} is not available — {desc} dependencies are not installed",'
            f'"code":"MODEL_MISSING",'
            f'"model":"{model}",'
            f'"solution":"Install with: {cmd}",'
            '"detail":"Restart the server after installing the missing packages"}'
        ),
        media_type="application/json",
        status_code=503,
    )


def _save_and_create_task(
    db: AsyncSession,
    session_id: str,
    model_type: str,
    file_content: bytes,
    original_name: str,
    confidence_threshold: float | None = None,
) -> tuple[Task, str]:
    """Save upload and create a PENDING task record. Returns (task, input_path)."""
    task_id = str(uuid.uuid4())
    input_path = file_manager.save_upload(session_id, task_id, file_content, original_name)

    task = Task(
        id=task_id,
        session_id=session_id,
        model_type=model_type,
        status=TaskStatus.PENDING.value,
        parameters={"confidence_threshold": confidence_threshold} if confidence_threshold else None,
    )
    db.add(task)
    return task, str(input_path)


@router.post(
    "/upload",
    response_model=None,
    responses={
        200: {"description": "Sync inference completed"},
        202: {"description": "Async task queued"},
        400: {"model": ErrorResponse, "description": "Validation error"},
    },
)
@limiter.limit("10/minute")
async def upload_image(
    request: Request,
    response: Response,
    file: UploadFile = File(...),
    model: str = Form(..., description="Model type: yolo, rembg, ocr"),
    mode: str = Form(default="sync", description="Execution mode: sync or async"),
    confidence_threshold: float | None = Form(default=None, ge=0.0, le=1.0),
    db: AsyncSession = Depends(get_db),
):
    session_id = _get_session_id(request, response)

    if model not in ("yolo", "rembg", "ocr"):
        return Response(
            content='{"error":"INVALID_MODEL","detail":"model must be one of: yolo, rembg, ocr"}',
            media_type="application/json",
            status_code=400,
        )

    if not model_registry.is_available(model):
        return _model_missing_response(model)

    try:
        content, detected_fmt = validate_upload(file)
    except ValidationError as e:
        return Response(
            content=f'{{"error":"{e.error_code}","detail":"{e.detail}"}}',
            media_type="application/json",
            status_code=400,
        )

    if mode == "async":
        return await _handle_async(
            db, session_id, model, content, file.filename or "image.png", confidence_threshold
        )

    try:
        result = await create_task(
            db=db,
            session_id=session_id,
            model_type=model,
            file_content=content,
            original_name=file.filename or "image.png",
            confidence_threshold=confidence_threshold,
        )
        return result
    except ImportError:
        return _model_missing_response(model)
    except TypeError:
        logger.exception("Internal serialization error")
        return Response(
            content='{"error":"INFERENCE_FAILED","detail":"Internal serialization error — please try again"}',
            media_type="application/json",
            status_code=500,
        )
    except Exception:
        logger.exception("Inference failed")
        return Response(
            content='{"error":"INFERENCE_FAILED","detail":"Inference failed — please try again"}',
            media_type="application/json",
            status_code=500,
        )


async def _handle_async(
    db: AsyncSession,
    session_id: str,
    model_type: str,
    file_content: bytes,
    original_name: str,
    confidence_threshold: float | None = None,
) -> Response:
    task, input_path = _save_and_create_task(
        db, session_id, model_type, file_content, original_name, confidence_threshold
    )
    task.started_at = datetime.now(timezone.utc)
    await db.flush()

    from celery_worker import celery_app

    celery_app.send_task(
        "inference.run",
        args=[task.id, session_id, model_type, input_path],
    )

    return Response(
        content=f'{{"task_id":"{task.id}","status":"PENDING","status_url":"/api/v1/tasks/{task.id}/status"}}',
        media_type="application/json",
        status_code=202,
    )
