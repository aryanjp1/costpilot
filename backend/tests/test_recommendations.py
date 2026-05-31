import uuid

from app.services import recommendation_service
from tests.conftest import make_api_key, seed_events


async def test_model_downgrade_recommendation(db, auth_client, project):
    _, api_key = await make_api_key(db, project["id"])
    specs = [{"model": "gpt-4o", "cost_usd": 1.0} for _ in range(150)]
    await seed_events(db, project["id"], api_key.id, specs)

    recs = await recommendation_service.get_recommendations(
        uuid.UUID(project["id"]), db
    )
    downgrades = [r for r in recs if r["type"] == "model_downgrade"]
    assert downgrades
    assert downgrades[0]["model_to"] == "gpt-4o-mini"
    assert downgrades[0]["estimated_savings_usd"] > 0


async def test_no_downgrade_below_threshold(db, auth_client, project):
    _, api_key = await make_api_key(db, project["id"])
    specs = [{"model": "gpt-4o", "cost_usd": 1.0} for _ in range(10)]
    await seed_events(db, project["id"], api_key.id, specs)

    recs = await recommendation_service.get_recommendations(
        uuid.UUID(project["id"]), db
    )
    assert not [r for r in recs if r["type"] == "model_downgrade"]


async def test_cost_concentration_recommendation(db, auth_client, project):
    _, api_key = await make_api_key(db, project["id"])
    specs = [{"cost_usd": 10.0, "tags": {"feature": "doc-summary"}}]
    specs += [{"cost_usd": 0.5, "tags": {"feature": "chat"}} for _ in range(3)]
    await seed_events(db, project["id"], api_key.id, specs)

    recs = await recommendation_service.get_recommendations(
        uuid.UUID(project["id"]), db
    )
    assert any(r["type"] == "cost_concentration" for r in recs)


async def test_error_waste_recommendation(db, auth_client, project):
    _, api_key = await make_api_key(db, project["id"])
    specs = [{"status": "success", "cost_usd": 1.0} for _ in range(80)]
    specs += [{"status": "error", "cost_usd": 1.0} for _ in range(20)]
    await seed_events(db, project["id"], api_key.id, specs)

    recs = await recommendation_service.get_recommendations(
        uuid.UUID(project["id"]), db
    )
    assert any(r["type"] == "error_waste" for r in recs)


async def test_prompt_optimization_recommendation(db, auth_client, project):
    _, api_key = await make_api_key(db, project["id"])
    specs = [{"input_tokens": 5000, "cost_usd": 1.0} for _ in range(5)]
    await seed_events(db, project["id"], api_key.id, specs)

    recs = await recommendation_service.get_recommendations(
        uuid.UUID(project["id"]), db
    )
    assert any(r["type"] == "prompt_optimization" for r in recs)
