import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    APP_NAME: str = "Negotiation Agent"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    DATABASE_URL: str = "sqlite:///./negotiation.db"

    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-1.5-flash"
    GEMINI_TIMEOUT: int = 30

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7


@lru_cache
def get_settings() -> Settings:
    return Settings()
