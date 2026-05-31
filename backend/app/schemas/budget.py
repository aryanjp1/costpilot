import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

ALLOWED_PERIODS = {"daily", "weekly", "monthly"}


class BudgetCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    period: str
    amount_usd: float = Field(gt=0)
    alert_threshold_pct: int = Field(default=80, ge=1, le=100)

    @field_validator("period")
    @classmethod
    def _check_period(cls, value: str) -> str:
        if value not in ALLOWED_PERIODS:
            raise ValueError(f"period must be one of {sorted(ALLOWED_PERIODS)}")
        return value


class BudgetUpdate(BaseModel):
    name: str | None = None
    period: str | None = None
    amount_usd: float | None = Field(default=None, gt=0)
    alert_threshold_pct: int | None = Field(default=None, ge=1, le=100)
    is_active: bool | None = None

    @field_validator("period")
    @classmethod
    def _check_period(cls, value: str | None) -> str | None:
        if value is not None and value not in ALLOWED_PERIODS:
            raise ValueError(f"period must be one of {sorted(ALLOWED_PERIODS)}")
        return value


class BudgetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    period: str
    amount_usd: float
    alert_threshold_pct: int
    is_active: bool
    created_at: datetime
