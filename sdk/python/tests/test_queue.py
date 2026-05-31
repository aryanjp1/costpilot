from costpilot.models import Event
from costpilot.queue import EventQueue


def make_event(model="gpt-4o"):
    return Event(
        model=model,
        input_tokens=10,
        output_tokens=20,
        cost_usd=0.001,
        latency_ms=100,
        status="success",
    )


def test_add_returns_false_until_batch_full():
    q = EventQueue(batch_size=3)
    assert q.add(make_event()) is False
    assert q.add(make_event()) is False
    assert q.add(make_event()) is True


def test_drain_returns_one_batch():
    q = EventQueue(batch_size=2)
    for _ in range(5):
        q.add(make_event())
    batch = q.drain()
    assert len(batch) == 2
    assert len(q) == 3


def test_drain_with_explicit_limit():
    q = EventQueue(batch_size=50)
    for _ in range(10):
        q.add(make_event())
    assert len(q.drain(4)) == 4
    assert len(q) == 6


def test_drain_empty():
    q = EventQueue()
    assert q.drain() == []


def test_len_tracks_pending():
    q = EventQueue(batch_size=100)
    assert len(q) == 0
    q.add(make_event())
    assert len(q) == 1
