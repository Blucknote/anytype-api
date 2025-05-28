"""Configuration management using Pydantic settings"""

from functools import lru_cache
from typing import Dict, List

from pydantic import AnyHttpUrl, Field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""

    # API Configuration
    api_title: str = "Anytype API"
    api_description: str = "FastAPI backend for Anytype integration"
    api_version: str = "1.0.1"

    # Anytype Configuration
    anytype_api_url: AnyHttpUrl = Field(default="http://localhost:31009", alias="ANYTYPE_API_URL")
    anytype_api_key: str = Field(alias="ANYTYPE_API_KEY")

    # CORS Configuration
    cors_origins: List[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]

    # Logging Configuration
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        alias="LOG_FORMAT",
    )
    log_file: str | None = Field(default=None, alias="LOG_FILE")
    log_rotation: str = Field(default="1 day", alias="LOG_ROTATION")
    log_retention: str = Field(default="7 days", alias="LOG_RETENTION")
    log_compression: str = Field(default="zip", alias="LOG_COMPRESSION")

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="allow",
        populate_by_name=True,
    )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
