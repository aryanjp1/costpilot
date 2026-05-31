import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..dependencies import get_current_user, get_project_for_user
from ..models.project import Project
from ..models.project_member import ProjectMember
from ..models.user import User
from ..schemas.project import MemberInvite, MemberOut, MemberUpdate
from ..services import auth_service

router = APIRouter(prefix="/projects", tags=["members"])

ALLOWED_ROLES = {"owner", "admin", "member"}


def _to_member_out(member: ProjectMember, user: User) -> MemberOut:
    return MemberOut(
        id=member.id,
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=member.role,
        joined_at=member.joined_at,
    )


async def _require_admin(project: Project, user: User, db: AsyncSession) -> None:
    if project.owner_id == user.id:
        return
    result = await db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project.id,
            ProjectMember.user_id == user.id,
        )
    )
    member = result.scalar_one_or_none()
    if member is None or member.role not in {"owner", "admin"}:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admin role required")


@router.get("/{project_id}/members", response_model=list[MemberOut])
async def list_members(
    project: Project = Depends(get_project_for_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ProjectMember, User)
        .join(User, User.id == ProjectMember.user_id)
        .where(ProjectMember.project_id == project.id)
        .order_by(ProjectMember.joined_at)
    )
    return [_to_member_out(member, user) for member, user in result.all()]


@router.post(
    "/{project_id}/members/invite",
    response_model=MemberOut,
    status_code=status.HTTP_201_CREATED,
)
async def invite_member(
    payload: MemberInvite,
    project: Project = Depends(get_project_for_user),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _require_admin(project, user, db)
    if payload.role not in ALLOWED_ROLES:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Invalid role")

    invited = await auth_service.get_user_by_email(db, payload.email)
    if invited is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, "No user with that email. Ask them to register."
        )

    existing = await db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project.id,
            ProjectMember.user_id == invited.id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status.HTTP_409_CONFLICT, "Already a member")

    member = ProjectMember(
        project_id=project.id, user_id=invited.id, role=payload.role
    )
    db.add(member)
    await db.commit()
    await db.refresh(member)
    return _to_member_out(member, invited)


@router.put("/{project_id}/members/{member_id}", response_model=MemberOut)
async def update_member(
    member_id: uuid.UUID,
    payload: MemberUpdate,
    project: Project = Depends(get_project_for_user),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _require_admin(project, user, db)
    if payload.role not in ALLOWED_ROLES:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Invalid role")

    member = await db.get(ProjectMember, member_id)
    if member is None or member.project_id != project.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Member not found")
    member.role = payload.role
    await db.commit()
    await db.refresh(member)

    member_user = await db.get(User, member.user_id)
    return _to_member_out(member, member_user)


@router.delete(
    "/{project_id}/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def remove_member(
    member_id: uuid.UUID,
    project: Project = Depends(get_project_for_user),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _require_admin(project, user, db)
    member = await db.get(ProjectMember, member_id)
    if member is None or member.project_id != project.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Member not found")
    if member.user_id == project.owner_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Cannot remove the owner")
    await db.delete(member)
    await db.commit()
