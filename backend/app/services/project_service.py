import hashlib
import re
import secrets
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.api_key import ApiKey
from ..models.project import Project
from ..models.project_member import ProjectMember
from ..models.user import User

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def _slugify(name: str) -> str:
    base = _SLUG_RE.sub("-", name.lower()).strip("-")
    return base or "project"


async def _unique_slug(db: AsyncSession, name: str) -> str:
    base = _slugify(name)
    slug = base
    suffix = 1
    while True:
        existing = await db.execute(select(Project).where(Project.slug == slug))
        if existing.scalar_one_or_none() is None:
            return slug
        suffix += 1
        slug = f"{base}-{suffix}"


async def create_project(
    db: AsyncSession, owner: User, name: str, description: str | None
) -> Project:
    project = Project(
        name=name,
        slug=await _unique_slug(db, name),
        description=description,
        owner_id=owner.id,
    )
    db.add(project)
    await db.flush()

    db.add(ProjectMember(project_id=project.id, user_id=owner.id, role="owner"))
    await db.commit()
    await db.refresh(project)
    return project


async def list_projects_for_user(db: AsyncSession, user: User) -> list[Project]:
    """Projects the user owns or is a member of."""
    member_projects = (
        select(ProjectMember.project_id)
        .where(ProjectMember.user_id == user.id)
        .scalar_subquery()
    )
    result = await db.execute(
        select(Project)
        .where((Project.owner_id == user.id) | (Project.id.in_(member_projects)))
        .order_by(Project.created_at.desc())
    )
    return list(result.scalars().unique().all())


# --- API keys ---------------------------------------------------------------


def generate_api_key() -> tuple[str, str, str]:
    """Return (full_key, key_hash, key_prefix)."""
    full_key = f"cp_proj_{secrets.token_hex(16)}"
    key_hash = hashlib.sha256(full_key.encode()).hexdigest()
    key_prefix = full_key[:12]
    return full_key, key_hash, key_prefix


async def create_api_key(
    db: AsyncSession, project_id: uuid.UUID, name: str
) -> tuple[ApiKey, str]:
    full_key, key_hash, key_prefix = generate_api_key()
    api_key = ApiKey(
        project_id=project_id,
        name=name,
        key_hash=key_hash,
        key_prefix=key_prefix,
    )
    db.add(api_key)
    await db.commit()
    await db.refresh(api_key)
    return api_key, full_key


async def list_api_keys(db: AsyncSession, project_id: uuid.UUID) -> list[ApiKey]:
    result = await db.execute(
        select(ApiKey)
        .where(ApiKey.project_id == project_id)
        .order_by(ApiKey.created_at.desc())
    )
    return list(result.scalars().all())
