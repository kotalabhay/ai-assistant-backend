"""Configuration settings for the application."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings using Pydantic BaseSettings.

    Attributes:
        api_v1_prefix: Prefix for API endpoints.
        project_name: Name of the project.
        allowed_origins: CORS allowed origins.
        secret_key: Secret key for JWT hashing.
        algorithm: Algorithm for JWT hashing.
        gemini_api_key: Internal API key for Google Gemini model.
        access_token_expire_minutes: Expiration time for access token in minutes.
    """

    api_v1_prefix: str = "/api/v1"
    project_name: str = "AI Assistant API"
    allowed_origins: list[str] = ["http://localhost:5173", "http://localhost"]
    
    secret_key: str = "test-secret-key-replace-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    
    admin_username: str = "admin"
    admin_password: str = "password123"
    
    gemini_api_key: str = ""
    llm_timeout_seconds: float = 30.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


settings = Settings()
