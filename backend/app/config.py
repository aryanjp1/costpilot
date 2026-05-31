from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://costpilot:costpilot_dev@localhost:5432/costpilot"
    secret_key: str = "change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7

    openai_api_key: str | None = None

    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    ingest_rate_limit_per_minute: int = 600


@lru_cache
def get_settings() -> Settings:
    return Settings()
