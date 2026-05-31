import time
from collections import defaultdict, deque

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import get_settings
from ..database import get_db
from ..dependencies import get_api_key
from ..models.api_key import ApiKey
from ..schemas.event import IngestPayload, IngestResult
from ..services import budget_service, ingest_service

router = APIRouter(tags=["ingest"])
settings = get_settings()

# Simple in-process sliding-window rate limiter, keyed per API key.
_WINDOW_SECONDS = 60
_hits: dict[str, deque[float]] = defaultdict(deque)


def _check_rate_limit(key_id: str) -> None:
    now = time.monotonic()
    bucket = _hits[key_id]
    while bucket and bucket[0] <= now - _WINDOW_SECONDS:
        bucket.popleft()
    if len(bucket) >= settings.ingest_rate_limit_per_minute:
        raise HTTPException(
            status.HTTP_429_TOO_MANY_REQUESTS, "Rate limit exceeded"
        )
    bucket.append(now)


@router.post("/ingest", response_model=IngestResult, status_code=status.HTTP_202_ACCEPTED)
async def ingest_events(
    payload: IngestPayload,
    background_tasks: BackgroundTasks,
    api_key: ApiKey = Depends(get_api_key),
    db: AsyncSession = Depends(get_db),
):
    _check_rate_limit(str(api_key.id))

    accepted = await ingest_service.store_events(
        db, api_key.project_id, api_key.id, payload.events
    )

    background_tasks.add_task(budget_service.check_budgets, api_key.project_id)
    return IngestResult(accepted=accepted)
