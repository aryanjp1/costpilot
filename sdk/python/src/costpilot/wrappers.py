import functools
import time
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from . import _state
from .models import Event
from .pricing import calculate_cost

if TYPE_CHECKING:
    import anthropic
    import openai

_TAG_HEADER = "x-costpilot-tags"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _extract_tags(extra_headers: dict | None) -> dict[str, str]:
    """Parse the ``x-costpilot-tags`` header into a {key: value} dict.

    Format is a comma separated list of "key:value" pairs, e.g.
    "feature:doc-summary,user:alice".
    """
    if not extra_headers:
        return {}
    raw = extra_headers.get(_TAG_HEADER)
    if not raw:
        return {}
    tags: dict[str, str] = {}
    for pair in raw.split(","):
        if ":" in pair:
            key, value = pair.split(":", 1)
            tags[key.strip()] = value.strip()
    return tags


def _merged_tags(call_tags: dict[str, str]) -> dict[str, str]:
    client = _state.get_client()
    base = client.default_tags if client else {}
    return {**base, **call_tags}


def _emit(event: Event) -> None:
    client = _state.get_client()
    if client is not None:
        client.track(event)


def wrap_openai(client: "openai.OpenAI") -> "openai.OpenAI":
    """Patch ``client.chat.completions.create`` to record every call.

    The original client is returned so callers can keep using it as before.
    """
    original_create = client.chat.completions.create

    @functools.wraps(original_create)
    def tracked_create(*args, **kwargs):
        tags = _merged_tags(_extract_tags(kwargs.get("extra_headers")))
        start = time.monotonic()
        try:
            response = original_create(*args, **kwargs)
        except Exception as exc:
            _emit(
                Event(
                    model=kwargs.get("model", "unknown"),
                    input_tokens=0,
                    output_tokens=0,
                    cost_usd=0.0,
                    latency_ms=int((time.monotonic() - start) * 1000),
                    status="error",
                    error_message=str(exc),
                    tags=tags,
                    timestamp=_now(),
                )
            )
            raise

        latency_ms = int((time.monotonic() - start) * 1000)
        model = getattr(response, "model", None) or kwargs.get("model", "unknown")
        usage = getattr(response, "usage", None)
        input_tokens = getattr(usage, "prompt_tokens", 0) if usage else 0
        output_tokens = getattr(usage, "completion_tokens", 0) if usage else 0
        _emit(
            Event(
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost_usd=calculate_cost(model, input_tokens, output_tokens),
                latency_ms=latency_ms,
                status="success",
                tags=tags,
                timestamp=_now(),
            )
        )
        return response

    client.chat.completions.create = tracked_create
    return client


def wrap_anthropic(client: "anthropic.Anthropic") -> "anthropic.Anthropic":
    """Patch ``client.messages.create`` to record every call."""
    original_create = client.messages.create

    @functools.wraps(original_create)
    def tracked_create(*args, **kwargs):
        tags = _merged_tags(_extract_tags(kwargs.get("extra_headers")))
        start = time.monotonic()
        try:
            response = original_create(*args, **kwargs)
        except Exception as exc:
            _emit(
                Event(
                    model=kwargs.get("model", "unknown"),
                    input_tokens=0,
                    output_tokens=0,
                    cost_usd=0.0,
                    latency_ms=int((time.monotonic() - start) * 1000),
                    status="error",
                    error_message=str(exc),
                    tags=tags,
                    timestamp=_now(),
                )
            )
            raise

        latency_ms = int((time.monotonic() - start) * 1000)
        model = getattr(response, "model", None) or kwargs.get("model", "unknown")
        usage = getattr(response, "usage", None)
        input_tokens = getattr(usage, "input_tokens", 0) if usage else 0
        output_tokens = getattr(usage, "output_tokens", 0) if usage else 0
        _emit(
            Event(
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost_usd=calculate_cost(model, input_tokens, output_tokens),
                latency_ms=latency_ms,
                status="success",
                tags=tags,
                timestamp=_now(),
            )
        )
        return response

    client.messages.create = tracked_create
    return client
