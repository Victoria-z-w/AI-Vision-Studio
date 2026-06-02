from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.limiter import limiter
from app.models import get_db
from app.schemas.task import TaskDeleteRequest
from app.services.task_service import delete_task, get_task, get_task_status, list_tasks
from app.storage.file_manager import file_manager
from app.utils.image import make_thumbnail

router = APIRouter()


def _get_session_id(request: Request) -> str:
    return request.cookies.get("session_id", "default")


@router.get("/tasks/{task_id}/status")
@limiter.limit("60/minute")
async def task_status(request: Request, task_id: str, db: AsyncSession = Depends(get_db)):
    status = await get_task_status(db, task_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return status


@router.get("/tasks/{task_id}/result.json")
async def task_result_json(task_id: str, request: Request):
    sid = _get_session_id(request)
    path = file_manager.get_path(sid, task_id, "result.json")
    if not path.exists():
        raise HTTPException(status_code=404, detail="Result not found")
    return FileResponse(path, media_type="application/json", filename="result.json")


@router.get("/tasks/{task_id}/visualization.png")
async def task_visualization(task_id: str, request: Request):
    sid = _get_session_id(request)
    path = file_manager.get_path(sid, task_id, "visualization.png")
    if not path.exists():
        raise HTTPException(status_code=404, detail="Visualization not found")
    return FileResponse(path, media_type="image/png")


@router.get("/tasks/{task_id}/foreground.png")
async def task_foreground(task_id: str, request: Request):
    sid = _get_session_id(request)
    path = file_manager.get_path(sid, task_id, "foreground.png")
    if not path.exists():
        raise HTTPException(status_code=404, detail="Foreground not found")
    return FileResponse(path, media_type="image/png")


@router.get("/tasks/{task_id}/thumbnail.jpg")
async def task_thumbnail(task_id: str, request: Request):
    sid = _get_session_id(request)
    # Find the input file in the task directory
    task_dir = file_manager.task_dir(sid, task_id)
    input_files = list(task_dir.glob("input_*"))
    if input_files:
        thumb = make_thumbnail(input_files[0])
        return Response(content=thumb.getvalue(), media_type="image/jpeg")
    raise HTTPException(status_code=404, detail="No image found")


@router.get("/tasks")
@limiter.limit("60/minute")
async def task_history(
    request: Request,
    model: str | None = Query(None),
    status: str | None = Query(None),
    q: str | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    sid = _get_session_id(request)
    return await list_tasks(db, sid, model=model, status=status, q=q, page=page, size=size)


@router.delete("/tasks/{task_id}")
async def task_delete(
    task_id: str, request: Request, db: AsyncSession = Depends(get_db)
):
    sid = _get_session_id(request)
    deleted = await delete_task(db, task_id, sid)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"status": "deleted"}


@router.delete("/tasks/batch")
async def task_batch_delete(
    body: TaskDeleteRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    sid = _get_session_id(request)
    for tid in body.task_ids:
        await delete_task(db, tid, sid)
    return {"deleted": len(body.task_ids)}
