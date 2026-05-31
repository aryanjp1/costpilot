import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..dependencies import get_current_user, get_project_for_user
from ..models.api_key import ApiKey
from ..models.project import Project
from ..models.user import User
from ..schemas.api_key import ApiKeyCreate, ApiKeyCreated, ApiKeyOut
from ..services import project_service

router = APIRouter(tags=["api-keys"])


@router.get("/projects/{project_id}/api-keys", response_model=list[ApiKeyOut])
async def list_keys(
    project: Project = Depends(get_project_for_user),
    db: AsyncSession = Depends(get_db),
):
    return await project_service.list_api_keys(db, project.id)


@router.post(
    "/projects/{project_id}/api-keys",
    response_model=ApiKeyCreated,
    status_code=status.HTTP_201_CREATED,
)
async def create_key(
    payload: ApiKeyCreate,
    project: Project = Depends(get_project_for_user),
    db: AsyncSession = Depends(get_db),
):
    api_key, full_key = await project_service.create_api_key(
        db, project.id, payload.name
    )
    return ApiKeyCreated(
        id=api_key.id,
        name=api_key.name,
        key_prefix=api_key.key_prefix,
        is_active=api_key.is_active,
        last_used_at=api_key.last_used_at,
        created_at=api_key.created_at,
        key=full_key,
    )


@router.delete("/api-keys/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_key(
    key_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    api_key = await db.get(ApiKey, key_id)
    if api_key is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "API key not found")

    project = await db.get(Project, api_key.project_id)
    if project is None or project.owner_id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not allowed")

    api_key.is_active = False
    await db.commit()
