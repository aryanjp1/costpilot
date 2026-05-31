from . import _state
from .client import CostPilotClient
from .models import Event
from .pricing import calculate_cost
from .wrappers import wrap_anthropic, wrap_openai

__version__ = "0.1.0"

__all__ = [
    "init",
    "flush",
    "wrap_openai",
    "wrap_anthropic",
    "calculate_cost",
    "Event",
    "CostPilotClient",
]


def init(
    api_key: str,
    endpoint: str = "http://localhost:8787",
    default_tags: dict[str, str] | None = None,
    flush_interval: float = 5.0,
    batch_size: int = 50,
) -> CostPilotClient:
    """Start the global CostPilot client. Call once at application startup."""
    client = CostPilotClient(
        api_key=api_key,
        endpoint=endpoint,
        default_tags=default_tags,
        flush_interval=flush_interval,
        batch_size=batch_size,
    )
    _state.set_client(client)
    return client


def flush() -> None:
    """Force-send any buffered events. Useful before a short script exits."""
    client = _state.get_client()
    if client is not None:
        client.flush()
