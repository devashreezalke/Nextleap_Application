import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    GROQ_API_KEY: str
    LOG_LEVEL: str = "info"
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    LLM_MODEL: str = "llama-3.1-8b-instant"
    BUDGET_LOW_MAX: int = 500
    BUDGET_MEDIUM_MAX: int = 1500
    DATA_PATH: str = "data/processed/restaurants.parquet"

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
