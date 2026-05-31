import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from ..models.event import Event
from ..schemas.event import IngestEvent

logger = logging.getLogger("costpilot.ingest")


def _parse_timestamp(raw: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(raw)
    except (ValueError, TypeError):
        return datetime.now(timezone.utc)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


async def store_events(
    db: AsyncSession,
    project_id: uuid.UUID,
    api_key_id: uuid.UUID,
    events: list[IngestEvent],
) -> int:
    """Bulk insert SDK events. Kept deliberately lean — this is the hot path."""
    rows = [
        Event(
            project_id=project_id,
            api_key_id=api_key_id,
            model=raw.model,
            input_tokens=raw.input_tokens,
            output_tokens=raw.output_tokens,
            cost_usd=raw.cost_usd,
            latency_ms=raw.latency_ms,
            status=raw.status,
            error_message=raw.error_message,
            tags=raw.tags,
            timestamp=_parse_timestamp(raw.timestamp),
        )
        for raw in events
    ]
    db.add_all(rows)
    await db.commit()
    return len(rows)
