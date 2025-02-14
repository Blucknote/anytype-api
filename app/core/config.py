"""Configuration management using Pydantic settings"""

from functools import lru_cache
from typing import List

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    api_title: str = "Anytype API"
    api_description: str = "FastAPI backend for Anytype integration"
    api_version: str = "1.0.0"
    
    # Anytype Configuration
    anytype_api_url: AnyHttpUrl = Field(alias="ANYTYPE_API_URL")
    anytype_session_token: str = Field(alias="ANYTYPE_SESSION_TOKEN")
    anytype_app_key: str = Field(alias="ANYTYPE_APP_KEY")
    
    # CORS Configuration
    cors_origins: List[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]

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
