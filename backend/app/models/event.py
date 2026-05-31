import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from ..database import Base

# JSONB on Postgres (indexable, supports ->> text extraction); plain JSON on SQLite.
TagsType = JSON().with_variant(JSONB(), "postgresql")


class Event(Base):
    __tablename__ = "events"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id"), index=True)
    api_key_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("api_keys.id"))

    model: Mapped[str] = mapped_column(String(100), index=True)
    input_tokens: Mapped[int] = mapped_column()
    output_tokens: Mapped[int] = mapped_column()
    cost_usd: Mapped[float] = mapped_column()
    latency_ms: Mapped[int] = mapped_column()
    status: Mapped[str] = mapped_column(String(20))
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    tags: Mapped[dict] = mapped_column(TagsType, default=dict)

    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now()
    )

    __table_args__ = (
        Index("ix_events_project_timestamp", "project_id", "timestamp"),
        Index("ix_events_project_model", "project_id", "model"),
    )
