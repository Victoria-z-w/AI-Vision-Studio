from __future__ import annotations

import time
import uuid
from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi import APIRouter, File, Form, Request, Response, UploadFile

from app.config import settings
from app.engine.registry import model_registry
from app.limiter import limiter
from app.preprocessing.pipeline import run_preprocessing
from app.utils.image import image_to_base64, numpy_to_native
from app.utils.validators import ValidationError, validate_upload

router = APIRouter()


@router.post("/infer")
@limiter.limit("10/minute")
async def infer(
    request: Request,
    file: UploadFile = File(...),
    model: str = Form(..., description="Model type: yolo, rembg, ocr"),
    confidence_threshold: float | None = Form(default=None, ge=0.0, le=1.0),
):
    """Run inference and return base64-encoded images in the JSON response.

    Returns:
        JSON with model-appropriate result fields and base64-encoded images.
        - yolo:    detections[], count, image_size, vis_base64
        - ocr:     regions[], full_text, region_count, image_size, vis_base64
        - rembg:   image_size, foreground_base64
    """
    if model not in ("yolo", "rembg", "ocr"):
        return Response(
            content='{"error":"INVALID_MODEL","detail":"model must be one of: yolo, rembg, ocr"}',
            media_type="application/json",
            status_code=400,
        )

    if not model_registry.is_available(model):
        from app.dependencies import get_install_command, get_model_description

        cmd = get_install_command(model) or f"pip install {model}"
        desc = get_model_description(model)
        return Response(
            content=(
                '{"error":"MODEL_UNAVAILABLE",'
                f'"message":"{model} is not available — {desc} dependencies missing",'
                f'"code":"MODEL_MISSING","model":"{model}",'
                f'"solution":"Install with: {cmd}"}}'
            ),
            media_type="application/json",
            status_code=503,
        )

    try:
        content, detected_fmt = validate_upload(file)
    except ValidationError as e:
        return Response(
            content=f'{{"error":"{e.error_code}","detail":"{e.detail}"}}',
            media_type="application/json",
            status_code=400,
        )

    task_id = str(uuid.uuid4())
    start_time = time.perf_counter()

    with TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir)

        # Save upload to temp
        input_path = tmp / f"input_{task_id[:8]}{Path(file.filename or 'image.png').suffix}"
        input_path.write_bytes(content)

        # Preprocessing
        preproc_dir = tmp / "preproc"
        preproc_path = run_preprocessing(input_path, preproc_dir)

        # Inference
        engine = model_registry.get_engine(model)
        infer_result = engine.infer(str(preproc_path), confidence_threshold=confidence_threshold)
        inference_time_ms = (time.perf_counter() - start_time) * 1000

        # Build JSON-safe response with base64 images
        response_data = {
            "task_id": task_id,
            "model": model,
            "status": "SUCCESS",
            "meta": {
                "inference_time_ms": round(inference_time_ms, 1),
                "device": model_registry.device,
                "model_version": getattr(engine, "version", "unknown"),
                "confidence_threshold": confidence_threshold
                or (
                    settings.CONFIDENCE_THRESHOLD
                    if model == "yolo"
                    else settings.OCR_CONFIDENCE_THRESHOLD
                ),
            },
        }

        if model == "yolo":
            response_data["result"] = {
                "detections": numpy_to_native(infer_result["detections"]),
                "count": infer_result["count"],
                "image_size": infer_result["image_size"],
            }
            from app.services.visualization import draw_yolo_boxes

            vis_img = draw_yolo_boxes(preproc_path, infer_result["detections"])
            response_data["vis_base64"] = image_to_base64(vis_img)

        elif model == "ocr":
            response_data["result"] = {
                "regions": numpy_to_native(infer_result["regions"]),
                "full_text": infer_result["full_text"],
                "region_count": infer_result["region_count"],
                "image_size": infer_result["image_size"],
            }
            from app.services.visualization import draw_ocr_boxes

            vis_img = draw_ocr_boxes(preproc_path, infer_result["regions"])
            response_data["vis_base64"] = image_to_base64(vis_img)

        elif model == "rembg":
            foreground_img = infer_result.pop("foreground", None)
            response_data["result"] = {
                "image_size": infer_result.get("image_size", {}),
            }
            if foreground_img is not None:
                response_data["foreground_base64"] = image_to_base64(foreground_img)

        return numpy_to_native(response_data)
