from datetime import datetime, timedelta, timezone

PERIOD_TO_DELTA = {
    "24h": timedelta(hours=24),
    "7d": timedelta(days=7),
    "30d": timedelta(days=30),
    "90d": timedelta(days=90),
}

VALID_GRANULARITIES = {"hour", "day", "week"}


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def calculate_start_time(period: str) -> datetime:
    """Translate a period label like "7d" into an absolute start time."""
    delta = PERIOD_TO_DELTA.get(period)
    if delta is None:
        raise ValueError(f"unknown period: {period}")
    return now_utc() - delta


def normalize_granularity(granularity: str) -> str:
    if granularity not in VALID_GRANULARITIES:
        raise ValueError(f"unknown granularity: {granularity}")
    return granularity


def get_period_start(period: str) -> datetime:
    """Start of the current budget window (day / week / month) in UTC."""
    now = now_utc()
    if period == "daily":
        return now.replace(hour=0, minute=0, second=0, microsecond=0)
    if period == "weekly":
        monday = now - timedelta(days=now.weekday())
        return monday.replace(hour=0, minute=0, second=0, microsecond=0)
    if period == "monthly":
        return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    raise ValueError(f"unknown budget period: {period}")
