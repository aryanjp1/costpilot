import uuid
from datetime import datetime

from sqlalchemy import Float, case, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.event import Event
from ..utils.time_utils import calculate_start_time, normalize_granularity, now_utc

# date_trunc lives in PostgreSQL. SQLite (used in tests) needs strftime instead,
# so we pick the bucket expression based on the dialect at query time.
_SQLITE_FORMATS = {
    "hour": "%Y-%m-%d %H:00:00",
    "day": "%Y-%m-%d 00:00:00",
    "week": "%Y-%W",
}


def _bucket_expr(db: AsyncSession, granularity: str):
    dialect = db.bind.dialect.name if db.bind else "postgresql"
    if dialect == "sqlite":
        return func.strftime(_SQLITE_FORMATS[granularity], Event.timestamp)
    return func.date_trunc(granularity, Event.timestamp)


def _bucket_label(value) -> str:
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


async def get_overview(
    project_id: uuid.UUID, period: str, db: AsyncSession
) -> dict:
    start_time = calculate_start_time(period)
    # Previous window: same length, immediately before the current one.
    span = now_utc() - start_time
    prev_start = start_time - span

    current = await _aggregate_window(project_id, start_time, None, db)
    previous = await _aggregate_window(project_id, prev_start, start_time, db)

    total_cost = current["total_cost"]
    total_requests = current["total_requests"]
    prev_cost = previous["total_cost"]

    cost_change_pct = 0.0
    if prev_cost > 0:
        cost_change_pct = round((total_cost - prev_cost) / prev_cost * 100, 1)

    return {
        "total_cost": round(total_cost, 4),
        "total_requests": total_requests,
        "avg_cost_per_request": round(total_cost / total_requests, 6)
        if total_requests
        else 0.0,
        "avg_latency": round(current["avg_latency"], 1),
        "models_used": current["models_used"],
        "error_rate": round(current["error_rate"], 2),
        "prev_total_cost": round(prev_cost, 4),
        "cost_change_pct": cost_change_pct,
    }


async def _aggregate_window(
    project_id: uuid.UUID,
    start_time: datetime,
    end_time: datetime | None,
    db: AsyncSession,
) -> dict:
    conditions = [Event.project_id == project_id, Event.timestamp >= start_time]
    if end_time is not None:
        conditions.append(Event.timestamp < end_time)

    error_flag = case((Event.status == "error", 1), else_=0)
    result = await db.execute(
        select(
            func.coalesce(func.sum(Event.cost_usd), 0.0),
            func.count(Event.id),
            func.coalesce(func.avg(Event.latency_ms), 0.0),
            func.count(func.distinct(Event.model)),
            func.coalesce(func.sum(error_flag), 0),
        ).where(*conditions)
    )
    total_cost, total_requests, avg_latency, models_used, errors = result.one()
    error_rate = (errors / total_requests * 100) if total_requests else 0.0
    return {
        "total_cost": float(total_cost),
        "total_requests": int(total_requests),
        "avg_latency": float(avg_latency),
        "models_used": int(models_used),
        "error_rate": error_rate,
    }


async def get_cost_timeline(
    project_id: uuid.UUID, period: str, granularity: str, db: AsyncSession
) -> list[dict]:
    start_time = calculate_start_time(period)
    granularity = normalize_granularity(granularity)
    bucket = _bucket_expr(db, granularity).label("bucket")

    result = await db.execute(
        select(
            bucket,
            func.sum(Event.cost_usd).label("cost"),
            func.count(Event.id).label("requests"),
        )
        .where(Event.project_id == project_id, Event.timestamp >= start_time)
        .group_by(bucket)
        .order_by(bucket)
    )
    return [
        {
            "timestamp": _bucket_label(row.bucket),
            "cost": round(float(row.cost), 4),
            "requests": int(row.requests),
        }
        for row in result.all()
    ]


async def get_model_breakdown(
    project_id: uuid.UUID, period: str, db: AsyncSession
) -> list[dict]:
    start_time = calculate_start_time(period)
    result = await db.execute(
        select(
            Event.model,
            func.sum(Event.cost_usd).label("cost"),
            func.count(Event.id).label("requests"),
            func.avg(Event.latency_ms).label("avg_latency"),
            func.sum(Event.input_tokens).label("input_tokens"),
            func.sum(Event.output_tokens).label("output_tokens"),
        )
        .where(Event.project_id == project_id, Event.timestamp >= start_time)
        .group_by(Event.model)
        .order_by(func.sum(Event.cost_usd).desc())
    )
    return [
        {
            "model": row.model,
            "cost": round(float(row.cost), 4),
            "requests": int(row.requests),
            "avg_latency": round(float(row.avg_latency), 1),
            "input_tokens": int(row.input_tokens),
            "output_tokens": int(row.output_tokens),
        }
        for row in result.all()
    ]


def _tag_value_expr(db: AsyncSession, tag_key: str):
    """Extract a single tag value out of the JSON tags column as text."""
    dialect = db.bind.dialect.name if db.bind else "postgresql"
    if dialect == "sqlite":
        return func.json_extract(Event.tags, f"$.{tag_key}")
    # jsonb_extract_path_text works on the jsonb column regardless of the type
    # SQLAlchemy infers for the variant column, so we avoid relying on .astext.
    return func.jsonb_extract_path_text(Event.tags, tag_key)


async def get_tag_breakdown(
    project_id: uuid.UUID, period: str, tag_key: str, db: AsyncSession
) -> list[dict]:
    start_time = calculate_start_time(period)
    tag_value = _tag_value_expr(db, tag_key).label("tag_value")

    result = await db.execute(
        select(
            tag_value,
            func.sum(Event.cost_usd).label("cost"),
            func.count(Event.id).label("requests"),
        )
        .where(
            Event.project_id == project_id,
            Event.timestamp >= start_time,
            tag_value.isnot(None),
        )
        .group_by(tag_value)
        .order_by(func.sum(Event.cost_usd).desc())
    )
    return [
        {
            "tag_value": row.tag_value,
            "cost": round(float(row.cost), 4),
            "requests": int(row.requests),
        }
        for row in result.all()
        if row.tag_value is not None
    ]


async def get_token_timeline(
    project_id: uuid.UUID, period: str, granularity: str, db: AsyncSession
) -> list[dict]:
    start_time = calculate_start_time(period)
    granularity = normalize_granularity(granularity)
    bucket = _bucket_expr(db, granularity).label("bucket")

    result = await db.execute(
        select(
            bucket,
            func.sum(Event.input_tokens).label("input_tokens"),
            func.sum(Event.output_tokens).label("output_tokens"),
        )
        .where(Event.project_id == project_id, Event.timestamp >= start_time)
        .group_by(bucket)
        .order_by(bucket)
    )
    return [
        {
            "timestamp": _bucket_label(row.bucket),
            "input_tokens": int(row.input_tokens),
            "output_tokens": int(row.output_tokens),
        }
        for row in result.all()
    ]


async def get_latency_timeline(
    project_id: uuid.UUID, period: str, granularity: str, db: AsyncSession
) -> list[dict]:
    start_time = calculate_start_time(period)
    granularity = normalize_granularity(granularity)
    bucket = _bucket_expr(db, granularity)
    dialect = db.bind.dialect.name if db.bind else "postgresql"

    if dialect == "sqlite":
        # SQLite has no percentile_cont; approximate with avg for the test path.
        result = await db.execute(
            select(
                bucket.label("bucket"),
                func.avg(Event.latency_ms).label("avg_latency"),
            )
            .where(Event.project_id == project_id, Event.timestamp >= start_time)
            .group_by(bucket)
            .order_by(bucket)
        )
        return [
            {
                "timestamp": _bucket_label(row.bucket),
                "p50": round(float(row.avg_latency), 1),
                "p95": round(float(row.avg_latency), 1),
                "p99": round(float(row.avg_latency), 1),
            }
            for row in result.all()
        ]

    latency = cast(Event.latency_ms, Float)
    result = await db.execute(
        select(
            bucket.label("bucket"),
            func.percentile_cont(0.5).within_group(latency).label("p50"),
            func.percentile_cont(0.95).within_group(latency).label("p95"),
            func.percentile_cont(0.99).within_group(latency).label("p99"),
        )
        .where(Event.project_id == project_id, Event.timestamp >= start_time)
        .group_by(bucket)
        .order_by(bucket)
    )
    return [
        {
            "timestamp": _bucket_label(row.bucket),
            "p50": round(float(row.p50), 1),
            "p95": round(float(row.p95), 1),
            "p99": round(float(row.p99), 1),
        }
        for row in result.all()
    ]


async def get_error_timeline(
    project_id: uuid.UUID, period: str, granularity: str, db: AsyncSession
) -> list[dict]:
    start_time = calculate_start_time(period)
    granularity = normalize_granularity(granularity)
    bucket = _bucket_expr(db, granularity).label("bucket")
    error_flag = case((Event.status == "error", 1), else_=0)

    result = await db.execute(
        select(
            bucket,
            func.sum(error_flag).label("error_count"),
            func.count(Event.id).label("total"),
        )
        .where(Event.project_id == project_id, Event.timestamp >= start_time)
        .group_by(bucket)
        .order_by(bucket)
    )
    out = []
    for row in result.all():
        total = int(row.total)
        errors = int(row.error_count)
        out.append(
            {
                "timestamp": _bucket_label(row.bucket),
                "error_count": errors,
                "error_rate": round(errors / total * 100, 2) if total else 0.0,
            }
        )
    return out


async def get_total_cost(
    project_id: uuid.UUID, since: datetime, db: AsyncSession
) -> float:
    result = await db.execute(
        select(func.coalesce(func.sum(Event.cost_usd), 0.0)).where(
            Event.project_id == project_id, Event.timestamp >= since
        )
    )
    return float(result.scalar_one())


async def get_error_rate(
    project_id: uuid.UUID, period: str, db: AsyncSession
) -> float:
    window = await _aggregate_window(project_id, calculate_start_time(period), None, db)
    return window["error_rate"]


async def get_avg_input_tokens(
    project_id: uuid.UUID, period: str, db: AsyncSession
) -> float:
    start_time = calculate_start_time(period)
    result = await db.execute(
        select(func.coalesce(func.avg(Event.input_tokens), 0.0)).where(
            Event.project_id == project_id, Event.timestamp >= start_time
        )
    )
    return float(result.scalar_one())
