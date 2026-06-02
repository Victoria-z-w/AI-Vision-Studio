from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

# Override settings for testing
os.environ["DB_URL"] = "sqlite+aiosqlite:///./test_data/test.db"
os.environ["UPLOAD_DIR"] = "./test_data/uploads"
os.environ["DEVICE"] = "cpu"

from app.main import create_app
from app.config import settings
from app.models import Base, engine, init_db

TEST_DIR = Path(__file__).parent
FIXTURES_DIR = TEST_DIR / "fixtures"


@pytest.fixture(autouse=True)
async def setup_db():
    """Create tables before each test, drop after."""
    await init_db()
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client():
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_image():
    """Create a simple test image."""
    from PIL import Image

    img = Image.new("RGB", (200, 200), color=(73, 109, 137))
    buf = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    img.save(buf, format="PNG")
    buf.close()
    yield Path(buf.name)
    Path(buf.name).unlink(missing_ok=True)
