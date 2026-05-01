from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./app/db/sqlite.db"
    gemini_api_key: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
