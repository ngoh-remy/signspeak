"""
SignSpeak Backend - Configuration
==================================
Loads configuration from environment variables (.env file).
Using pydantic-settings ensures type safety and validation.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str = "signspeak-dev-secret-key-2025"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    DATABASE_URL: str = "sqlite:///./signspeak.db"
    AI_MODEL_DIR: str = "../Ai_model"
    FRONTEND_URL: str = ""  # Set in production (e.g. https://signspeak.vercel.app)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
