import hashlib

from app.services import project_service


def test_generated_key_format():
    full_key, key_hash, prefix = project_service.generate_api_key()
    assert full_key.startswith("cp_proj_")
    assert len(full_key) == len("cp_proj_") + 32
    assert key_hash == hashlib.sha256(full_key.encode()).hexdigest()
    assert prefix == full_key[:12]


def test_keys_are_unique():
    keys = {project_service.generate_api_key()[0] for _ in range(100)}
    assert len(keys) == 100


async def test_create_key_returns_full_key_once(auth_client, project):
    resp = await auth_client.post(
        f"/api/projects/{project['id']}/api-keys", json={"name": "Production"}
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["key"].startswith("cp_proj_")
    assert body["key_prefix"] == body["key"][:12]


async def test_list_keys_hides_plaintext(auth_client, project):
    await auth_client.post(
        f"/api/projects/{project['id']}/api-keys", json={"name": "Staging"}
    )
    resp = await auth_client.get(f"/api/projects/{project['id']}/api-keys")
    assert resp.status_code == 200
    keys = resp.json()
    assert len(keys) == 1
    assert "key" not in keys[0]
    assert keys[0]["key_prefix"].startswith("cp_proj_")


async def test_revoke_key(auth_client, project):
    created = await auth_client.post(
        f"/api/projects/{project['id']}/api-keys", json={"name": "Temp"}
    )
    key_id = created.json()["id"]
    resp = await auth_client.delete(f"/api/api-keys/{key_id}")
    assert resp.status_code == 204

    keys = (await auth_client.get(f"/api/projects/{project['id']}/api-keys")).json()
    assert keys[0]["is_active"] is False
