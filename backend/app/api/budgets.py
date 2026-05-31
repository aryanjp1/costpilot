import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..dependencies import get_current_user, get_project_for_user
from ..models.budget import Budget
from ..models.project import Project
from ..models.user import User
from ..schemas.analytics import Forecast
from ..schemas.budget import BudgetCreate, BudgetOut, BudgetUpdate
from ..services import forecast_service

router = APIRouter(tags=["budgets"])


@router.get("/projects/{project_id}/forecast", response_model=Forecast)
async def get_forecast(
    project: Project = Depends(get_project_for_user),
    db: AsyncSession = Depends(get_db),
):
    return await forecast_service.get_forecast(project.id, db)


@router.get("/projects/{project_id}/budgets", response_model=list[BudgetOut])
async def list_budgets(
    project: Project = Depends(get_project_for_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Budget)
        .where(Budget.project_id == project.id)
        .order_by(Budget.created_at.desc())
    )
    return list(result.scalars().all())


@router.post(
    "/projects/{project_id}/budgets",
    response_model=BudgetOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_budget(
    payload: BudgetCreate,
    project: Project = Depends(get_project_for_user),
    db: AsyncSession = Depends(get_db),
):
    budget = Budget(
        project_id=project.id,
        name=payload.name,
        period=payload.period,
        amount_usd=payload.amount_usd,
        alert_threshold_pct=payload.alert_threshold_pct,
    )
    db.add(budget)
    await db.commit()
    await db.refresh(budget)
    return budget


async def _load_budget_for_user(
    budget_id: uuid.UUID, user: User, db: AsyncSession
) -> Budget:
    budget = await db.get(Budget, budget_id)
    if budget is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Budget not found")
    project = await db.get(Project, budget.project_id)
    if project is None or project.owner_id != user.id:
        # Members can read analytics, but mutating budgets is owner-only here.
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not allowed")
    return budget


@router.put("/budgets/{budget_id}", response_model=BudgetOut)
async def update_budget(
    budget_id: uuid.UUID,
    payload: BudgetUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    budget = await _load_budget_for_user(budget_id, user, db)
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(budget, field, value)
    await db.commit()
    await db.refresh(budget)
    return budget


@router.delete("/budgets/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_budget(
    budget_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    budget = await _load_budget_for_user(budget_id, user, db)
    await db.delete(budget)
    await db.commit()
