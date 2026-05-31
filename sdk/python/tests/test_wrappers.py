from types import SimpleNamespace

import pytest

import costpilot
from costpilot import _state
from costpilot.wrappers import _extract_tags, wrap_anthropic, wrap_openai


class RecordingClient:
    """Stand-in for the global client that just stores tracked events."""

    def __init__(self):
        self.default_tags = {}
        self.events = []

    def track(self, event):
        self.events.append(event)


@pytest.fixture
def recorder():
    client = RecordingClient()
    _state.set_client(client)
    yield client
    _state.set_client(None)


def make_openai_stub():
    usage = SimpleNamespace(prompt_tokens=100, completion_tokens=50)
    response = SimpleNamespace(model="gpt-4o", usage=usage)

    def create(*args, **kwargs):
        return response

    completions = SimpleNamespace(create=create)
    chat = SimpleNamespace(completions=completions)
    return SimpleNamespace(chat=chat), response


def make_anthropic_stub():
    usage = SimpleNamespace(input_tokens=200, output_tokens=80)
    response = SimpleNamespace(model="claude-sonnet-4-6", usage=usage)

    def create(*args, **kwargs):
        return response

    messages = SimpleNamespace(create=create)
    return SimpleNamespace(messages=messages), response


def test_extract_tags_parses_pairs():
    tags = _extract_tags({"x-costpilot-tags": "feature:doc-summary,user:alice"})
    assert tags == {"feature": "doc-summary", "user": "alice"}


def test_extract_tags_empty():
    assert _extract_tags(None) == {}
    assert _extract_tags({}) == {}


def test_openai_call_is_transparent(recorder):
    client, response = make_openai_stub()
    wrapped = wrap_openai(client)
    result = wrapped.chat.completions.create(model="gpt-4o", messages=[])
    assert result is response


def test_openai_call_tracks_event(recorder):
    client, _ = make_openai_stub()
    wrapped = wrap_openai(client)
    wrapped.chat.completions.create(model="gpt-4o", messages=[])
    assert len(recorder.events) == 1
    event = recorder.events[0]
    assert event.model == "gpt-4o"
    assert event.input_tokens == 100
    assert event.output_tokens == 50
    assert event.status == "success"
    assert event.cost_usd > 0


def test_openai_merges_default_and_call_tags(recorder):
    recorder.default_tags = {"service": "chatbot"}
    client, _ = make_openai_stub()
    wrapped = wrap_openai(client)
    wrapped.chat.completions.create(
        model="gpt-4o",
        messages=[],
        extra_headers={"x-costpilot-tags": "feature:doc-summary"},
    )
    assert recorder.events[0].tags == {"service": "chatbot", "feature": "doc-summary"}


def test_openai_error_tracks_and_reraises(recorder):
    def failing_create(*args, **kwargs):
        raise RuntimeError("rate limited")

    client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=failing_create))
    )
    wrapped = wrap_openai(client)
    with pytest.raises(RuntimeError):
        wrapped.chat.completions.create(model="gpt-4o", messages=[])
    assert recorder.events[0].status == "error"
    assert "rate limited" in recorder.events[0].error_message


def test_anthropic_call_tracks_event(recorder):
    client, _ = make_anthropic_stub()
    wrapped = wrap_anthropic(client)
    wrapped.messages.create(model="claude-sonnet-4-6", messages=[], max_tokens=10)
    event = recorder.events[0]
    assert event.model == "claude-sonnet-4-6"
    assert event.input_tokens == 200
    assert event.output_tokens == 80


def test_no_client_does_not_crash():
    _state.set_client(None)
    client, response = make_openai_stub()
    wrapped = wrap_openai(client)
    # No global client registered — call should still pass through cleanly.
    assert wrapped.chat.completions.create(model="gpt-4o", messages=[]) is response
