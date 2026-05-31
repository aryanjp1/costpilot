from .client import CostPilotClient

_client: CostPilotClient | None = None


def set_client(client: CostPilotClient) -> None:
    global _client
    _client = client


def get_client() -> CostPilotClient | None:
    return _client
