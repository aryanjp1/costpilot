import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..dependencies import get_current_user, get_project_for_user
from ..models.alert import Alert
from ..models.budget import Budget
from ..models.project import Project
from ..models.user import User
from ..schemas.alert import AlertOut

router = APIRouter(tags=["alerts"])


@router.get("/projects/{project_id}/alerts", response_model=list[AlertOut])
async def list_alerts(
    unread_only: bool = Query(default=False),
    limit: int = Query(default=50, ge=1, le=200),
    project: Project = Depends(get_project_for_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Alert).where(Alert.project_id == project.id)
    if unread_only:
        query = query.where(Alert.is_read.is_(False))
    query = query.order_by(Alert.created_at.desc()).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())


@router.put("/alerts/{alert_id}/read", response_model=AlertOut)
async def mark_read(
    alert_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    alert = await db.get(Alert, alert_id)
    if alert is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Alert not found")
    project = await db.get(Project, alert.project_id)
    if project is None or project.owner_id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not allowed")
    alert.is_read = True
    await db.commit()
    await db.refresh(alert)
    return alert
