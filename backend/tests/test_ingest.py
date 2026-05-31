from datetime import datetime, timezone

from sqlalchemy import func, select

from app.models.event import Event
from tests.conftest import make_api_key


def _event_payload(**overrides):
    base = {
        "model": "gpt-4o",
        "input_tokens": 1000,
        "output_tokens": 500,
        "cost_usd": 0.0075,
        "latency_ms": 420,
        "status": "success",
        "tags": {"feature": "chat"},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    base.update(overrides)
    return base


async def test_ingest_stores_events(auth_client, project, db):
    full_key, _ = await make_api_key(db, project["id"])
    resp = await auth_client.post(
        "/api/ingest",
        json={"events": [_event_payload(), _event_payload(model="gpt-4o-mini")]},
        headers={"Authorization": f"Bearer {full_key}"},
    )
    assert resp.status_code == 202
    assert resp.json()["accepted"] == 2

    count = await db.scalar(select(func.count(Event.id)))
    assert count == 2


async def test_ingest_rejects_bad_key(auth_client):
    resp = await auth_client.post(
        "/api/ingest",
        json={"events": []},
        headers={"Authorization": "Bearer cp_proj_doesnotexist"},
    )
    assert resp.status_code == 401


async def test_ingest_rejects_non_costpilot_token(auth_client):
    resp = await auth_client.post(
        "/api/ingest",
        json={"events": []},
        headers={"Authorization": "Bearer some-random-jwt"},
    )
    assert resp.status_code == 401


async def test_ingest_associates_project(auth_client, project, db):
    full_key, api_key = await make_api_key(db, project["id"])
    await auth_client.post(
        "/api/ingest",
        json={"events": [_event_payload()]},
        headers={"Authorization": f"Bearer {full_key}"},
    )
    event = (await db.execute(select(Event))).scalar_one()
    assert str(event.project_id) == project["id"]
    assert event.api_key_id == api_key.id


async def test_ingest_updates_last_used(auth_client, project, db):
    from app.models.api_key import ApiKey

    full_key, api_key = await make_api_key(db, project["id"])
    await auth_client.post(
        "/api/ingest",
        json={"events": [_event_payload()]},
        headers={"Authorization": f"Bearer {full_key}"},
    )
    refreshed = await db.get(ApiKey, api_key.id)
    await db.refresh(refreshed)
    assert refreshed.last_used_at is not None
