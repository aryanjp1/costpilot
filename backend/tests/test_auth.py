import uuid


async def test_register_and_login(client):
    email = f"new_{uuid.uuid4().hex[:8]}@example.com"
    resp = await client.post(
        "/api/auth/register",
        json={"email": email, "password": "password123", "full_name": "Alice"},
    )
    assert resp.status_code == 201
    assert resp.json()["email"] == email

    login = await client.post(
        "/api/auth/login", json={"email": email, "password": "password123"}
    )
    assert login.status_code == 200
    assert "access_token" in login.json()


async def test_duplicate_email_rejected(client):
    email = f"dup_{uuid.uuid4().hex[:8]}@example.com"
    payload = {"email": email, "password": "password123"}
    await client.post("/api/auth/register", json=payload)
    resp = await client.post("/api/auth/register", json=payload)
    assert resp.status_code == 409


async def test_login_wrong_password(client):
    email = f"wp_{uuid.uuid4().hex[:8]}@example.com"
    await client.post(
        "/api/auth/register", json={"email": email, "password": "password123"}
    )
    resp = await client.post(
        "/api/auth/login", json={"email": email, "password": "wrong-password"}
    )
    assert resp.status_code == 401


async def test_me_requires_token(client):
    resp = await client.get("/api/auth/me")
    assert resp.status_code == 401


async def test_me_returns_current_user(auth_client):
    resp = await auth_client.get("/api/auth/me")
    assert resp.status_code == 200
    assert "email" in resp.json()


async def test_short_password_rejected(client):
    resp = await client.post(
        "/api/auth/register", json={"email": "x@example.com", "password": "short"}
    )
    assert resp.status_code == 422
