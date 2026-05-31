from pydantic import BaseModel


class Recommendation(BaseModel):
    type: str
    title: str
    description: str
    estimated_savings_usd: float
    model_from: str | None = None
    model_to: str | None = None
    affected_tags: list[str] = []
