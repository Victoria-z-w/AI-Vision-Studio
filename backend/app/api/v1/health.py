from fastapi import APIRouter

from app.engine.registry import model_registry

router = APIRouter()


@router.get("/healthz")
async def healthz():
    model_status = model_registry.get_status()
    available_models = [
        name for name, entry in model_registry._engines.items()
        if model_registry.is_available(name)
    ]
    return {
        "status": "ok",
        "redis": "not_configured",
        "db": "connected",
        "models": model_status,
        "available_models": available_models,
    }
