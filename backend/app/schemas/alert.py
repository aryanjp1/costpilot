import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AlertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    budget_id: uuid.UUID
    alert_type: str
    title: str
    description: str
    current_spend: float
    budget_amount: float
    is_read: bool
    created_at: datetime
