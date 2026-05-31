import uuid
from datetime import datetime, timedelta, timezone

from app.services import forecast_service
from tests.conftest import make_api_key, seed_events


async def test_insufficient_data(db, auth_client, project):
    _, api_key = await make_api_key(db, project["id"])
    await seed_events(db, project["id"], api_key.id, [{"cost_usd": 0.1}])
    result = await forecast_service.get_forecast(uuid.UUID(project["id"]), db)
    assert result["trend"] == "insufficient_data"


async def test_projection_from_daily_average(db, auth_client, project):
    _, api_key = await make_api_key(db, project["id"])
    now = datetime.now(timezone.utc)
    specs = [
        {"cost_usd": 10.0, "timestamp": now - timedelta(days=d)} for d in range(7)
    ]
    await seed_events(db, project["id"], api_key.id, specs)

    result = await forecast_service.get_forecast(uuid.UUID(project["id"]), db)
    assert result["current_daily_avg"] == 10.0
    assert result["projected_weekly"] == 70.0
    assert result["projected_monthly"] == 300.0


async def test_increasing_trend(db, auth_client, project):
    _, api_key = await make_api_key(db, project["id"])
    now = datetime.now(timezone.utc)
    specs = []
    # First week low, second week high.
    for d in range(7, 14):
        specs.append({"cost_usd": 5.0, "timestamp": now - timedelta(days=d)})
    for d in range(0, 7):
        specs.append({"cost_usd": 20.0, "timestamp": now - timedelta(days=d)})
    await seed_events(db, project["id"], api_key.id, specs)

    result = await forecast_service.get_forecast(uuid.UUID(project["id"]), db)
    assert result["trend"] == "increasing"
