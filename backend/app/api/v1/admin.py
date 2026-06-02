from __future__ import annotations

from fastapi import APIRouter, Request

from app.engine.registry import model_registry
from app.limiter import limiter

router = APIRouter()


@router.get("/admin/models/status")
@limiter.limit("30/minute")
async def models_status(request: Request):
    return {
        "models": model_registry.get_status(),
        "device_available": [model_registry.device],
    }


@router.post("/admin/models/unload")
@limiter.limit("5/minute")
async def unload_model(request: Request, model: str):
    if model not in ("yolo", "rembg", "ocr"):
        return {"error": f"Unknown model: {model}"}, 400
    model_registry.unload(model)
    return {"status": "unloaded", "model": model}
