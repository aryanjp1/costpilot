import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from ..utils.pricing import DOWNGRADE_TARGETS
from . import analytics_service


async def get_recommendations(
    project_id: uuid.UUID, db: AsyncSession
) -> list[dict]:
    recommendations: list[dict] = []

    model_stats = await analytics_service.get_model_breakdown(project_id, "30d", db)
    recommendations.extend(_model_downgrade_recs(model_stats))

    feature_stats = await analytics_service.get_tag_breakdown(
        project_id, "30d", "feature", db
    )
    concentration = _cost_concentration_rec(feature_stats)
    if concentration:
        recommendations.append(concentration)

    error_rate = await analytics_service.get_error_rate(project_id, "30d", db)
    if error_rate > 5:
        total_cost = await analytics_service.get_total_cost(
            project_id, analytics_service.calculate_start_time("30d"), db
        )
        wasted = total_cost * (error_rate / 100)
        recommendations.append(
            {
                "type": "error_waste",
                "title": f"{error_rate:.1f}% error rate is costing you "
                f"${wasted:.2f}/month",
                "description": f"Failed requests still incur token costs. "
                f"Reducing your error rate from {error_rate:.1f}% to 2% would "
                f"save approximately ${wasted * 0.6:.2f}/month. Check your most "
                f"common error patterns in the logs.",
                "estimated_savings_usd": round(wasted * 0.6, 2),
            }
        )

    avg_tokens = await analytics_service.get_avg_input_tokens(project_id, "30d", db)
    if avg_tokens > 3000:
        total_cost = await analytics_service.get_total_cost(
            project_id, analytics_service.calculate_start_time("30d"), db
        )
        recommendations.append(
            {
                "type": "prompt_optimization",
                "title": f"Average input is {avg_tokens:,.0f} tokens — consider "
                f"prompt compression",
                "description": "Long prompts drive costs up. Review your system "
                "prompts for redundancy, use few-shot examples sparingly, and "
                "consider prompt compression techniques.",
                "estimated_savings_usd": round(total_cost * 0.15, 2),
            }
        )

    return recommendations


def _model_downgrade_recs(model_stats: list[dict]) -> list[dict]:
    recs = []
    thresholds = {"gpt-4o": 100, "claude-opus-4-7": 50, "gpt-4.1": 100}
    savings_ratio = {"gpt-4o": 0.85, "claude-opus-4-7": 0.70, "gpt-4.1": 0.80}

    for stat in model_stats:
        model = stat["model"]
        target = DOWNGRADE_TARGETS.get(model)
        if not target:
            continue
        if stat["requests"] < thresholds.get(model, 100):
            continue
        gross = stat["cost"] * savings_ratio.get(model, 0.7)
        recs.append(
            {
                "type": "model_downgrade",
                "title": f"Consider {target} for some {model} tasks",
                "description": f"You're spending ${stat['cost']:.2f}/month on "
                f"{model} across {stat['requests']} requests. For simpler tasks "
                f"(classification, extraction, short responses), {target} delivers "
                f"comparable quality at a fraction of the cost.",
                "estimated_savings_usd": round(gross * 0.3, 2),
                "model_from": model,
                "model_to": target,
            }
        )
    return recs


def _cost_concentration_rec(feature_stats: list[dict]) -> dict | None:
    if not feature_stats:
        return None
    total = sum(f["cost"] for f in feature_stats)
    if total <= 0:
        return None
    top = max(feature_stats, key=lambda f: f["cost"])
    if top["cost"] <= total * 0.5:
        return None
    share = int(top["cost"] / total * 100)
    return {
        "type": "cost_concentration",
        "title": f"Feature '{top['tag_value']}' accounts for {share}% of total cost",
        "description": f"${top['cost']:.2f}/month on a single feature. Consider "
        f"caching frequent responses, reducing max_tokens, or switching to a "
        f"cheaper model for this feature specifically.",
        "estimated_savings_usd": round(top["cost"] * 0.2, 2),
        "affected_tags": [top["tag_value"]],
    }
