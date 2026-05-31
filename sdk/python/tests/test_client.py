import time

import pytest

from costpilot.client import CostPilotClient
from costpilot.models import Event


def make_event():
    return Event(
        model="gpt-4o",
        input_tokens=10,
        output_tokens=20,
        cost_usd=0.001,
        latency_ms=100,
        status="success",
    )


@pytest.fixture
def captured(monkeypatch):
    sent: list[list[dict]] = []

    class FakeResponse:
        status_code = 202

    def fake_post(url, json, headers, timeout):
        sent.append(json["events"])
        return FakeResponse()

    import httpx

    monkeypatch.setattr(httpx, "post", fake_post)
    return sent


def test_batch_full_triggers_send(captured):
    client = CostPilotClient("cp_proj_test", "http://x", batch_size=3, flush_interval=999)
    for _ in range(3):
        client.track(make_event())
    time.sleep(0.2)
    assert len(captured) == 1
    assert len(captured[0]) == 3


def test_flush_sends_pending(captured):
    client = CostPilotClient("cp_proj_test", "http://x", batch_size=50, flush_interval=999)
    client.track(make_event())
    client.track(make_event())
    client.flush()
    time.sleep(0.2)
    assert sum(len(b) for b in captured) == 2


def test_auth_header_is_set(monkeypatch):
    seen = {}

    def fake_post(url, json, headers, timeout):
        seen["headers"] = headers
        seen["url"] = url

        class R:
            status_code = 202

        return R()

    import httpx

    monkeypatch.setattr(httpx, "post", fake_post)
    client = CostPilotClient("cp_proj_secret", "http://host:8787", batch_size=1, flush_interval=999)
    client.track(make_event())
    time.sleep(0.2)
    assert seen["headers"]["Authorization"] == "Bearer cp_proj_secret"
    assert seen["url"] == "http://host:8787/api/ingest"


def test_track_never_raises_when_backend_down(monkeypatch):
    def boom(*args, **kwargs):
        raise ConnectionError("backend is down")

    import httpx

    monkeypatch.setattr(httpx, "post", boom)
    client = CostPilotClient("cp_proj_test", "http://x", batch_size=1, flush_interval=999)
    # Should not raise even though every send blows up.
    client.track(make_event())
    time.sleep(0.2)


def test_endpoint_trailing_slash_stripped():
    client = CostPilotClient("k", "http://x:8787/", flush_interval=999)
    assert client.endpoint == "http://x:8787"
