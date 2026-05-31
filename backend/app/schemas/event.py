import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class IngestEvent(BaseModel):
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    latency_ms: int = 0
    status: str = "success"
    error_message: str | None = None
    tags: dict[str, str] = Field(default_factory=dict)
    timestamp: str


class IngestPayload(BaseModel):
    events: list[IngestEvent]


class IngestResult(BaseModel):
    accepted: int


class EventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    latency_ms: int
    status: str
    error_message: str | None
    tags: dict
    timestamp: datetime


class EventPage(BaseModel):
    items: list[EventOut]
    total: int
    page: int
    page_size: int
