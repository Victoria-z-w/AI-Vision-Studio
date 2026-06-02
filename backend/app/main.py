from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api import api_router
from app.config import settings
from app.dependencies import check_optional_dependencies
from app.engine.registry import model_registry
from app.limiter import limiter
from app.models import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    await init_db()

    # Register CV engines (lazy-loaded on first use)
    from app.engine.ocr import _create_ocr_engine
    from app.engine.rembg_engine import _create_rembg_engine
    from app.engine.yolo import _create_yolo_engine

    model_registry.register("yolo", _create_yolo_engine)
    model_registry.register("rembg", _create_rembg_engine)
    model_registry.register("ocr", _create_ocr_engine)

    # Check optional model dependencies — never crashes, only warns
    availability = check_optional_dependencies()
    model_registry.set_availability(availability)
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(SlowAPIMiddleware)

    app.include_router(api_router)

    return app


app = create_app()
