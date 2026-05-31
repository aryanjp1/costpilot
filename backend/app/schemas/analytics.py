from pydantic import BaseModel


class OverviewStats(BaseModel):
    total_cost: float
    total_requests: int
    avg_cost_per_request: float
    avg_latency: float
    models_used: int
    error_rate: float
    prev_total_cost: float
    cost_change_pct: float


class TimelinePoint(BaseModel):
    timestamp: str
    cost: float
    requests: int


class ModelStat(BaseModel):
    model: str
    cost: float
    requests: int
    avg_latency: float
    input_tokens: int
    output_tokens: int


class TagStat(BaseModel):
    tag_value: str
    cost: float
    requests: int


class TokenPoint(BaseModel):
    timestamp: str
    input_tokens: int
    output_tokens: int


class LatencyPoint(BaseModel):
    timestamp: str
    p50: float
    p95: float
    p99: float


class ErrorPoint(BaseModel):
    timestamp: str
    error_count: int
    error_rate: float


class Forecast(BaseModel):
    current_daily_avg: float
    projected_weekly: float
    projected_monthly: float
    trend: str
