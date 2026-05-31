import uuid
from datetime import datetime, timedelta, timezone

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base, get_db
from app.main import app
from app.models.api_key import ApiKey
from app.models.event import Event
from app.services import project_service

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def engine():
    engine = create_async_engine(TEST_DB_URL, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def session_factory(engine):
    return async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


@pytest_asyncio.fixture
async def db(session_factory):
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def client(session_factory):
    async def override_get_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def auth_client(client):
    """A client already registered, logged in, and carrying a bearer token."""
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    await client.post(
        "/api/auth/register",
        json={"email": email, "password": "password123", "full_name": "Test User"},
    )
    login = await client.post(
        "/api/auth/login", json={"email": email, "password": "password123"}
    )
    token = login.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client


@pytest_asyncio.fixture
async def project(auth_client):
    resp = await auth_client.post("/api/projects", json={"name": "Demo Project"})
    return resp.json()


async def make_api_key(db: AsyncSession, project_id) -> tuple[str, ApiKey]:
    api_key, full_key = await project_service.create_api_key(
        db, uuid.UUID(project_id), "Test Key"
    )
    return full_key, api_key


async def seed_events(db: AsyncSession, project_id, api_key_id, specs):
    """Insert events. ``specs`` is a list of dicts overriding defaults."""
    now = datetime.now(timezone.utc)
    rows = []
    for i, spec in enumerate(specs):
        rows.append(
            Event(
                project_id=uuid.UUID(project_id),
                api_key_id=api_key_id,
                model=spec.get("model", "gpt-4o"),
                input_tokens=spec.get("input_tokens", 1000),
                output_tokens=spec.get("output_tokens", 500),
                cost_usd=spec.get("cost_usd", 0.01),
                latency_ms=spec.get("latency_ms", 500),
                status=spec.get("status", "success"),
                error_message=spec.get("error_message"),
                tags=spec.get("tags", {}),
                timestamp=spec.get("timestamp", now - timedelta(hours=i)),
            )
        )
    db.add_all(rows)
    await db.commit()
    return rows
