from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..dependencies import get_project_for_user
from ..models.project import Project
from ..schemas.recommendation import Recommendation
from ..services import recommendation_service

router = APIRouter(prefix="/projects/{project_id}", tags=["recommendations"])


@router.get("/recommendations", response_model=list[Recommendation])
async def list_recommendations(
    project: Project = Depends(get_project_for_user),
    db: AsyncSession = Depends(get_db),
):
    return await recommendation_service.get_recommendations(project.id, db)
