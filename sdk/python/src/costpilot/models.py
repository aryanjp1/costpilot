from dataclasses import dataclass, asdict, field


@dataclass
class Event:
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    latency_ms: int
    status: str
    tags: dict[str, str] = field(default_factory=dict)
    timestamp: str = ""
    error_message: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)
