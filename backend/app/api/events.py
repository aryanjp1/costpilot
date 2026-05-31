from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..dependencies import get_project_for_user
from ..models.event import Event
from ..models.project import Project
from ..schemas.event import EventPage

router = APIRouter(prefix="/projects/{project_id}", tags=["events"])


@router.get("/events", response_model=EventPage)
async def list_events(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    model: str | None = Query(default=None),
    status: str | None = Query(default=None),
    start: datetime | None = Query(default=None),
    end: datetime | None = Query(default=None),
    project: Project = Depends(get_project_for_user),
    db: AsyncSession = Depends(get_db),
):
    filters = [Event.project_id == project.id]
    if model:
        filters.append(Event.model == model)
    if status:
        filters.append(Event.status == status)
    if start:
        filters.append(Event.timestamp >= start)
    if end:
        filters.append(Event.timestamp <= end)

    total = await db.scalar(
        select(func.count(Event.id)).where(*filters)
    )

    result = await db.execute(
        select(Event)
        .where(*filters)
        .order_by(Event.timestamp.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    return EventPage(
        items=list(result.scalars().all()),
        total=int(total or 0),
        page=page,
        page_size=page_size,
    )
