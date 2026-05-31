import logging
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import SessionLocal
from ..models.alert import Alert
from ..models.budget import Budget
from ..utils.time_utils import get_period_start
from . import analytics_service

logger = logging.getLogger("costpilot.budget")


async def get_active_budgets(
    db: AsyncSession, project_id: uuid.UUID
) -> list[Budget]:
    result = await db.execute(
        select(Budget).where(
            Budget.project_id == project_id, Budget.is_active.is_(True)
        )
    )
    return list(result.scalars().all())


async def _already_alerted(
    db: AsyncSession, budget: Budget, alert_type: str, period_start
) -> bool:
    """True if an alert of this type already fired in the current window."""
    result = await db.execute(
        select(Alert.id).where(
            Alert.budget_id == budget.id,
            Alert.alert_type == alert_type,
            Alert.created_at >= period_start,
        )
    )
    return result.first() is not None


async def _create_alert(
    db: AsyncSession,
    project_id: uuid.UUID,
    budget: Budget,
    alert_type: str,
    title: str,
    description: str,
    current_spend: float,
) -> None:
    db.add(
        Alert(
            project_id=project_id,
            budget_id=budget.id,
            alert_type=alert_type,
            title=title,
            description=description,
            current_spend=current_spend,
            budget_amount=budget.amount_usd,
        )
    )
    await db.commit()


async def evaluate_budgets(db: AsyncSession, project_id: uuid.UUID) -> None:
    budgets = await get_active_budgets(db, project_id)

    for budget in budgets:
        period_start = get_period_start(budget.period)
        current_spend = await analytics_service.get_total_cost(
            project_id, period_start, db
        )
        if budget.amount_usd <= 0:
            continue
        pct_used = current_spend / budget.amount_usd * 100

        if pct_used >= 100 and not await _already_alerted(
            db, budget, "exceeded", period_start
        ):
            await _create_alert(
                db,
                project_id,
                budget,
                "exceeded",
                f"Budget exceeded: {budget.name}",
                f"Current spend ${current_spend:.2f} exceeds {budget.period} "
                f"budget of ${budget.amount_usd:.2f}",
                current_spend,
            )
        elif pct_used >= budget.alert_threshold_pct and not await _already_alerted(
            db, budget, "warning", period_start
        ):
            await _create_alert(
                db,
                project_id,
                budget,
                "warning",
                f"Budget warning: {budget.name}",
                f"Current spend ${current_spend:.2f} is {pct_used:.0f}% of "
                f"{budget.period} budget (${budget.amount_usd:.2f})",
                current_spend,
            )


async def check_budgets(project_id: uuid.UUID) -> None:
    """Background-task entrypoint. Opens its own session."""
    try:
        async with SessionLocal() as db:
            await evaluate_budgets(db, project_id)
    except Exception:
        logger.exception("budget check failed for project %s", project_id)
