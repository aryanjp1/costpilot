from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..dependencies import get_project_for_user
from ..models.project import Project
from ..schemas.analytics import (
    ErrorPoint,
    Forecast,
    LatencyPoint,
    ModelStat,
    OverviewStats,
    TagStat,
    TimelinePoint,
    TokenPoint,
)
from ..services import analytics_service, forecast_service
from ..utils.time_utils import PERIOD_TO_DELTA, VALID_GRANULARITIES

router = APIRouter(prefix="/projects/{project_id}/analytics", tags=["analytics"])

PeriodQuery = Query(default="7d")
GranularityQuery = Query(default="hour")


def _validate_period(period: str) -> str:
    if period not in PERIOD_TO_DELTA:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            f"period must be one of {sorted(PERIOD_TO_DELTA)}",
        )
    return period


def _validate_granularity(granularity: str) -> str:
    if granularity not in VALID_GRANULARITIES:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            f"granularity must be one of {sorted(VALID_GRANULARITIES)}",
        )
    return granularity


@router.get("/overview", response_model=OverviewStats)
async def overview(
    period: str = PeriodQuery,
    project: Project = Depends(get_project_for_user),
    db: AsyncSession = Depends(get_db),
):
    return await analytics_service.get_overview(project.id, _validate_period(period), db)


@router.get("/cost-timeline", response_model=list[TimelinePoint])
async def cost_timeline(
    period: str = PeriodQuery,
    granularity: str = GranularityQuery,
    project: Project = Depends(get_project_for_user),
    db: AsyncSession = Depends(get_db),
):
    return await analytics_service.get_cost_timeline(
        project.id, _validate_period(period), _validate_granularity(granularity), db
    )


@router.get("/models", response_model=list[ModelStat])
async def models(
    period: str = PeriodQuery,
    project: Project = Depends(get_project_for_user),
    db: AsyncSession = Depends(get_db),
):
    return await analytics_service.get_model_breakdown(
        project.id, _validate_period(period), db
    )


@router.get("/tags", response_model=list[TagStat])
async def tags(
    period: str = PeriodQuery,
    tag_key: str = Query(default="feature"),
    project: Project = Depends(get_project_for_user),
    db: AsyncSession = Depends(get_db),
):
    return await analytics_service.get_tag_breakdown(
        project.id, _validate_period(period), tag_key, db
    )


@router.get("/members", response_model=list[TagStat])
async def members(
    period: str = PeriodQuery,
    project: Project = Depends(get_project_for_user),
    db: AsyncSession = Depends(get_db),
):
    return await analytics_service.get_tag_breakdown(
        project.id, _validate_period(period), "user", db
    )


@router.get("/tokens", response_model=list[TokenPoint])
async def tokens(
    period: str = PeriodQuery,
    granularity: str = GranularityQuery,
    project: Project = Depends(get_project_for_user),
    db: AsyncSession = Depends(get_db),
):
    return await analytics_service.get_token_timeline(
        project.id, _validate_period(period), _validate_granularity(granularity), db
    )


@router.get("/latency", response_model=list[LatencyPoint])
async def latency(
    period: str = PeriodQuery,
    granularity: str = GranularityQuery,
    project: Project = Depends(get_project_for_user),
    db: AsyncSession = Depends(get_db),
):
    return await analytics_service.get_latency_timeline(
        project.id, _validate_period(period), _validate_granularity(granularity), db
    )


@router.get("/errors", response_model=list[ErrorPoint])
async def errors(
    period: str = PeriodQuery,
    granularity: str = GranularityQuery,
    project: Project = Depends(get_project_for_user),
    db: AsyncSession = Depends(get_db),
):
    return await analytics_service.get_error_timeline(
        project.id, _validate_period(period), _validate_granularity(granularity), db
    )
