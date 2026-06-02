# AI Vision Studio

Lightweight computer vision full-stack workbench. Upload images → run YOLO/rembg/OCR inference → visualize results.

![Backend CI](https://github.com/OWNER/ai-vision-studio/actions/workflows/ci-backend.yml/badge.svg)
![Frontend CI](https://github.com/OWNER/ai-vision-studio/actions/workflows/ci-frontend.yml/badge.svg)

## Features

- **Object Detection** — YOLOv8n, 80 COCO classes with bounding box visualization
- **Background Removal** — rembg, foreground extraction with before/after comparison
- **Text Recognition** — PaddleOCR, Chinese/English text detection and extraction
- **REST API** — FastAPI with auto-generated Swagger UI (`/docs`)
- **Modern Frontend** — Vue 3 + TypeScript + Element Plus
- **Docker Compose** — One-command startup for the full stack

## Quick Start

### Prerequisites

- Docker & Docker Compose v2
- 4 GB RAM (8 GB recommended for all models)

### One-Command Startup

```bash
cp .env.example .env
docker compose up -d
```

Then open:
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/healthz

### Local Development

**Backend:**

```bash
cd backend
cp ../.env.example .env
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## Architecture

```
Vue 3 Frontend  ←→  FastAPI  ←→  CV Engines (YOLO / rembg / PaddleOCR)
     :5173             :8000              │
                                    ┌─────┴─────┐
                                    SQLite / PG  Redis
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/healthz` | Health check with model status |
| `POST` | `/api/v1/upload` | Upload image + run inference |
| `GET` | `/api/v1/tasks/{id}/status` | Get task status & results |
| `GET` | `/api/v1/tasks/{id}/visualization.png` | Download annotated image |
| `GET` | `/api/v1/tasks/{id}/foreground.png` | Download foreground (rembg) |
| `GET` | `/api/v1/tasks/{id}/result.json` | Download raw JSON result |
| `GET` | `/api/v1/tasks` | List task history |
| `DELETE` | `/api/v1/tasks/{id}` | Delete a task |
| `GET` | `/api/v1/admin/models/status` | Model loading status |

Full API documentation at `/docs` (Swagger UI).

## Configuration

All settings via environment variables (see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `DEVICE` | `auto` | `auto` / `cpu` / `cuda` |
| `MAX_FILE_SIZE_MB` | `20` | Max upload file size |
| `MAX_IMAGE_DIMENSION` | `4096` | Max image long edge in pixels |
| `CONFIDENCE_THRESHOLD` | `0.25` | YOLO detection threshold |
| `OCR_CONFIDENCE_THRESHOLD` | `0.5` | OCR recognition threshold |
| `DB_URL` | `sqlite+aiosqlite:///./data/avs.db` | Database connection string |

## GPU Support

Set `DEVICE=cuda` in `.env`. Requires NVIDIA Container Toolkit for Docker:

```bash
docker compose -f docker-compose.yml -f docker-compose.gpu.yml up -d
```

## Running Tests

```bash
# Backend
cd backend && python -m pytest tests/ -v

# Frontend
cd frontend && npx vitest run
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12 / FastAPI / SQLAlchemy / Celery |
| Frontend | Vue 3 / Vite / TypeScript / Element Plus / Pinia |
| CV Models | Ultralytics YOLOv8n / rembg / PaddleOCR |
| Infrastructure | Docker Compose / Redis / Nginx |
| CI/CD | GitHub Actions |

## Project Status

- [x] MVP: Upload + sync inference + visualization + history
- [ ] V1.0: Async tasks (Celery) + WebSocket progress + rate limiting
- [ ] V1.5: GPU detection + batch upload + dark mode + cloud deploy guide

## License

MIT
