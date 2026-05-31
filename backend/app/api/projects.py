import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..dependencies import get_current_user, get_project_for_user
from ..models.project import Project
from ..models.user import User
from ..schemas.project import ProjectCreate, ProjectOut, ProjectUpdate
from ..services import project_service

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=list[ProjectOut])
async def list_projects(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    return await project_service.list_projects_for_user(db, user)


@router.post("", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ProjectCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await project_service.create_project(
        db, user, payload.name, payload.description
    )


@router.get("/{project_id}", response_model=ProjectOut)
async def get_project(project: Project = Depends(get_project_for_user)):
    return project


@router.put("/{project_id}", response_model=ProjectOut)
async def update_project(
    payload: ProjectUpdate,
    project: Project = Depends(get_project_for_user),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if project.owner_id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only the owner can edit")
    if payload.name is not None:
        project.name = payload.name
    if payload.description is not None:
        project.description = payload.description
    await db.commit()
    await db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project: Project = Depends(get_project_for_user),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if project.owner_id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only the owner can delete")
    await db.delete(project)
    await db.commit()
