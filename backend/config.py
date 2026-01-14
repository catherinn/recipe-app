from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # API Keys (optional for test mode)
    anthropic_api_key: str = "test-key"
    google_client_id: str = "test-client-id"
    google_client_secret: str = ""

    # Database
    database_url: str = "sqlite:///./recipe_app.db"

    # JWT
    jwt_secret_key: str = "default-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days

    # App Config
    frontend_url: str = "http://localhost:5173"
    backend_url: str = "http://localhost:8000"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
