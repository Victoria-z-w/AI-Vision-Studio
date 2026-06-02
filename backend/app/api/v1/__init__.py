from fastapi import APIRouter

from app.api.v1.health import router as health_router
from app.api.v1.infer import router as infer_router
from app.api.v1.upload import router as upload_router
from app.api.v1.tasks import router as tasks_router
from app.api.v1.admin import router as admin_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health_router, tags=["health"])
api_router.include_router(infer_router, tags=["infer"])
api_router.include_router(upload_router, tags=["upload"])
api_router.include_router(tasks_router, tags=["tasks"])
api_router.include_router(admin_router, tags=["admin"])
