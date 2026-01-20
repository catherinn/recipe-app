from pydantic_settings import BaseSettings
from functools import lru_cache
import os
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    # API Keys - provide defaults so app can start, validate when actually used
    anthropic_api_key: str = ""
    google_client_id: str = ""
    google_client_secret: str = ""

    # Database
    database_url: str = "sqlite:///./recipe_app.db"

    # JWT - generate a default for development, but warn if not set
    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days

    # App Config
    frontend_url: str = "http://localhost:5173"
    backend_url: str = "http://localhost:8000"

    class Config:
        env_file = ".env"

    def validate_for_auth(self) -> None:
        """Validate settings required for authentication"""
        missing = []
        if not self.jwt_secret_key:
            missing.append("JWT_SECRET_KEY")
        if missing:
            raise ValueError(f"Missing required environment variables for auth: {', '.join(missing)}")

    def validate_for_google_auth(self) -> None:
        """Validate settings required for Google OAuth"""
        missing = []
        if not self.google_client_id:
            missing.append("GOOGLE_CLIENT_ID")
        if missing:
            raise ValueError(f"Missing required environment variables for Google auth: {', '.join(missing)}")

    def validate_for_ai(self) -> None:
        """Validate settings required for AI features"""
        if not self.anthropic_api_key:
            raise ValueError("Missing required environment variable: ANTHROPIC_API_KEY")


@lru_cache()
def get_settings():
    settings = Settings()
    # Log warnings for missing critical settings
    if not settings.anthropic_api_key:
        logger.warning("ANTHROPIC_API_KEY not set - AI features will not work")
    if not settings.google_client_id:
        logger.warning("GOOGLE_CLIENT_ID not set - Google OAuth will not work")
    if not settings.jwt_secret_key:
        logger.warning("JWT_SECRET_KEY not set - Authentication will not work")
    return settings
