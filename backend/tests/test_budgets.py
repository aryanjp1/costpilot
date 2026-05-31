from datetime import datetime, timezone

from app.services import budget_service
from tests.conftest import make_api_key, seed_events


async def test_create_and_list_budget(auth_client, project):
    resp = await auth_client.post(
        f"/api/projects/{project['id']}/budgets",
        json={"name": "Daily cap", "period": "daily", "amount_usd": 200},
    )
    assert resp.status_code == 201
    listed = await auth_client.get(f"/api/projects/{project['id']}/budgets")
    assert len(listed.json()) == 1


async def test_invalid_period_rejected(auth_client, project):
    resp = await auth_client.post(
        f"/api/projects/{project['id']}/budgets",
        json={"name": "Bad", "period": "yearly", "amount_usd": 10},
    )
    assert resp.status_code == 422


async def test_update_budget(auth_client, project):
    created = await auth_client.post(
        f"/api/projects/{project['id']}/budgets",
        json={"name": "Cap", "period": "monthly", "amount_usd": 1000},
    )
    budget_id = created.json()["id"]
    resp = await auth_client.put(
        f"/api/budgets/{budget_id}", json={"amount_usd": 2000}
    )
    assert resp.status_code == 200
    assert resp.json()["amount_usd"] == 2000


async def test_delete_budget(auth_client, project):
    created = await auth_client.post(
        f"/api/projects/{project['id']}/budgets",
        json={"name": "Cap", "period": "monthly", "amount_usd": 1000},
    )
    budget_id = created.json()["id"]
    resp = await auth_client.delete(f"/api/budgets/{budget_id}")
    assert resp.status_code == 204


async def test_exceeded_budget_creates_alert(auth_client, project, db):
    _, api_key = await make_api_key(db, project["id"])
    now = datetime.now(timezone.utc)
    await seed_events(
        db,
        project["id"],
        api_key.id,
        [{"cost_usd": 150.0, "timestamp": now}, {"cost_usd": 60.0, "timestamp": now}],
    )
    await auth_client.post(
        f"/api/projects/{project['id']}/budgets",
        json={"name": "Daily", "period": "daily", "amount_usd": 200},
    )
    await budget_service.evaluate_budgets(db, __import__("uuid").UUID(project["id"]))

    alerts = (await auth_client.get(f"/api/projects/{project['id']}/alerts")).json()
    assert any(a["alert_type"] == "exceeded" for a in alerts)


async def test_warning_budget_creates_alert(auth_client, project, db):
    import uuid

    _, api_key = await make_api_key(db, project["id"])
    now = datetime.now(timezone.utc)
    await seed_events(
        db, project["id"], api_key.id, [{"cost_usd": 170.0, "timestamp": now}]
    )
    await auth_client.post(
        f"/api/projects/{project['id']}/budgets",
        json={
            "name": "Daily",
            "period": "daily",
            "amount_usd": 200,
            "alert_threshold_pct": 80,
        },
    )
    await budget_service.evaluate_budgets(db, uuid.UUID(project["id"]))

    alerts = (await auth_client.get(f"/api/projects/{project['id']}/alerts")).json()
    assert any(a["alert_type"] == "warning" for a in alerts)


async def test_alert_not_duplicated(auth_client, project, db):
    import uuid

    _, api_key = await make_api_key(db, project["id"])
    now = datetime.now(timezone.utc)
    await seed_events(
        db, project["id"], api_key.id, [{"cost_usd": 250.0, "timestamp": now}]
    )
    await auth_client.post(
        f"/api/projects/{project['id']}/budgets",
        json={"name": "Daily", "period": "daily", "amount_usd": 200},
    )
    pid = uuid.UUID(project["id"])
    await budget_service.evaluate_budgets(db, pid)
    await budget_service.evaluate_budgets(db, pid)

    alerts = (await auth_client.get(f"/api/projects/{project['id']}/alerts")).json()
    exceeded = [a for a in alerts if a["alert_type"] == "exceeded"]
    assert len(exceeded) == 1
