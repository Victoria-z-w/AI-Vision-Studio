from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"), env_file_encoding="utf-8"
    )

    # App
    APP_NAME: str = "AI-Vision-Studio"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Database
    DB_URL: str = "sqlite+aiosqlite:///./data/avs.db"

    # File Storage
    UPLOAD_DIR: str = "./data/uploads"
    MAX_FILE_SIZE_MB: int = 20
    MAX_IMAGE_DIMENSION: int = 4096

    # CV Engine
    DEVICE: str = "auto"  # auto / cpu / cuda
    CONFIDENCE_THRESHOLD: float = 0.25
    OCR_CONFIDENCE_THRESHOLD: float = 0.5
    INFERENCE_TIMEOUT_S: int = 60
    PRELOAD_MODELS: bool = False

    # Redis / Celery
    REDIS_URL: str = "redis://localhost:6379/0"

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # Rate Limiting
    RATE_LIMIT: str = "60/minute"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()
