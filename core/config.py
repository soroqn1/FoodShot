from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings powered by Pydantic.
    Loads variables from .env file or environment.
    """

    # Telegram Bot
    BOT_TOKEN: str

    # AI & Vision
    OPENAI_API_KEY: str

    # Nutrition APIs
    USDA_API_KEY: Optional[str] = None
    NUTRITIONIX_APP_ID: Optional[str] = None
    NUTRITIONIX_API_KEY: Optional[str] = None

    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str

    # Webhook & Server
    WEBHOOK_URL: str
    PORT: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


config = Settings()
