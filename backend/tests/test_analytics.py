from datetime import datetime, timedelta, timezone

from tests.conftest import make_api_key, seed_events


async def _setup(auth_client, project, db, specs):
    _, api_key = await make_api_key(db, project["id"])
    await seed_events(db, project["id"], api_key.id, specs)


async def test_overview_totals(auth_client, project, db):
    await _setup(
        auth_client,
        project,
        db,
        [
            {"cost_usd": 0.10, "status": "success"},
            {"cost_usd": 0.20, "status": "success"},
            {"cost_usd": 0.00, "status": "error"},
        ],
    )
    resp = await auth_client.get(
        f"/api/projects/{project['id']}/analytics/overview?period=7d"
    )
    assert resp.status_code == 200
    data = resp.json()
    assert round(data["total_cost"], 2) == 0.30
    assert data["total_requests"] == 3
    assert round(data["error_rate"], 1) == round(100 / 3, 1)


async def test_model_breakdown_sorted_by_cost(auth_client, project, db):
    await _setup(
        auth_client,
        project,
        db,
        [
            {"model": "gpt-4o", "cost_usd": 0.50},
            {"model": "gpt-4o", "cost_usd": 0.30},
            {"model": "gpt-4o-mini", "cost_usd": 0.05},
        ],
    )
    resp = await auth_client.get(
        f"/api/projects/{project['id']}/analytics/models?period=7d"
    )
    data = resp.json()
    assert data[0]["model"] == "gpt-4o"
    assert round(data[0]["cost"], 2) == 0.80
    assert data[0]["requests"] == 2
    assert data[1]["model"] == "gpt-4o-mini"


async def test_tag_breakdown_by_feature(auth_client, project, db):
    await _setup(
        auth_client,
        project,
        db,
        [
            {"cost_usd": 0.40, "tags": {"feature": "doc-summary"}},
            {"cost_usd": 0.10, "tags": {"feature": "chat"}},
            {"cost_usd": 0.05, "tags": {"feature": "chat"}},
        ],
    )
    resp = await auth_client.get(
        f"/api/projects/{project['id']}/analytics/tags?period=7d&tag_key=feature"
    )
    data = resp.json()
    assert data[0]["tag_value"] == "doc-summary"
    assert round(data[0]["cost"], 2) == 0.40
    chat = next(d for d in data if d["tag_value"] == "chat")
    assert chat["requests"] == 2


async def test_cost_timeline_buckets(auth_client, project, db):
    now = datetime.now(timezone.utc)
    await _setup(
        auth_client,
        project,
        db,
        [
            {"cost_usd": 0.10, "timestamp": now - timedelta(days=1)},
            {"cost_usd": 0.20, "timestamp": now - timedelta(days=2)},
        ],
    )
    resp = await auth_client.get(
        f"/api/projects/{project['id']}/analytics/cost-timeline?period=7d&granularity=day"
    )
    data = resp.json()
    assert len(data) == 2
    assert round(sum(p["cost"] for p in data), 2) == 0.30


async def test_invalid_period_rejected(auth_client, project):
    resp = await auth_client.get(
        f"/api/projects/{project['id']}/analytics/overview?period=bogus"
    )
    assert resp.status_code == 422


async def test_members_breakdown_uses_user_tag(auth_client, project, db):
    await _setup(
        auth_client,
        project,
        db,
        [
            {"cost_usd": 0.30, "tags": {"user": "alice"}},
            {"cost_usd": 0.10, "tags": {"user": "bob"}},
        ],
    )
    resp = await auth_client.get(
        f"/api/projects/{project['id']}/analytics/members?period=7d"
    )
    data = resp.json()
    assert data[0]["tag_value"] == "alice"


async def test_error_timeline(auth_client, project, db):
    await _setup(
        auth_client,
        project,
        db,
        [
            {"status": "error", "cost_usd": 0.0},
            {"status": "success", "cost_usd": 0.1},
        ],
    )
    resp = await auth_client.get(
        f"/api/projects/{project['id']}/analytics/errors?period=7d&granularity=day"
    )
    assert resp.status_code == 200
    data = resp.json()
    assert sum(p["error_count"] for p in data) == 1
