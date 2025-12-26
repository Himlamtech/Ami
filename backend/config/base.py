"""
Base configuration - Core application settings.
All settings are loaded from environment variables via pydantic-settings.

Note: pydantic-settings automatically maps environment variables to field names
(case-insensitive). For example, field `app_port` maps to env var `APP_PORT`.
"""

from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    """Base configuration shared across all config modules."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


class AppConfig(BaseConfig):
    """Core application configuration."""

    # Application
    app_name: str = Field(default="AMI RAG System")
    app_port: int = Field(default=11121, ge=1, le=65535)
    debug: bool = Field(default=False)
    environment: Literal["development", "staging", "production"] = Field(
        default="development"
    )

    # Admin API Key (for protected admin routes)
    admin_api_key: str = Field(default="")

    # AI Services API Keys
    gemini_api_key: str = Field(default="")

    # CORS Configuration
    cors_origins: str = Field(default="http://localhost:11120,http://localhost:11121")

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]


# Singleton instance
app_config = AppConfig()
