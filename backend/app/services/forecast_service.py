import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from . import analytics_service


async def get_forecast(project_id: uuid.UUID, db: AsyncSession) -> dict:
    daily_costs = await analytics_service.get_cost_timeline(
        project_id, "30d", "day", db
    )

    if len(daily_costs) < 3:
        return {
            "current_daily_avg": 0.0,
            "projected_weekly": 0.0,
            "projected_monthly": 0.0,
            "trend": "insufficient_data",
        }

    costs = [point["cost"] for point in daily_costs]

    recent_7 = costs[-7:] if len(costs) >= 7 else costs
    daily_avg = sum(recent_7) / len(recent_7)

    trend = "stable"
    if len(costs) >= 14:
        first_half = sum(costs[-14:-7]) / 7
        second_half = sum(costs[-7:]) / 7
        if second_half > first_half * 1.15:
            trend = "increasing"
        elif second_half < first_half * 0.85:
            trend = "decreasing"

    return {
        "current_daily_avg": round(daily_avg, 2),
        "projected_weekly": round(daily_avg * 7, 2),
        "projected_monthly": round(daily_avg * 30, 2),
        "trend": trend,
    }
