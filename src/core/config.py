"""
Core configuration and settings for DhakaSmart platform.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
EPW_DIR = DATA_DIR / "weather"
CLIMATE_DIR = DATA_DIR / "climate"


class Settings(BaseSettings):
    """Application settings from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="DHAKA_", extra="ignore")

    # Database
    database_url: str = Field(
        default="postgresql+psycopg2://dhaka:dhaka@localhost:5432/dhaka_smart",
        description="SQLAlchemy database URL",
    )

    # API
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    api_prefix: str = Field(default="/api/v1", description="API route prefix")

    # Security
    secret_key: str = Field(default="dev-secret-change-in-production", description="JWT secret")
    access_token_expire_minutes: int = Field(default=30, description="Token expiry")
    api_key: Optional[str] = Field(default=None, description="Optional API key for external services")

    # AI (Phase 2)
    gemini_api_key: Optional[str] = Field(default=None, description="Gemini API key for AI assistant")
    ai_enabled: bool = Field(default=False, description="Enable AI assistant")

    # File upload
    max_upload_size_mb: int = Field(default=10, description="Max upload size in MB")
    allowed_ifc_extensions: tuple[str, ...] = (".ifc",)

    # EPW
    epw_dir: Path = Field(default=EPW_DIR, description="EPW weather data directory")

    # Emission factor defaults
    default_emission_factor_source: str = Field(
        default="DoE-GEF",
        description="Default grid emission factor source",
    )

    # Logging
    log_level: str = Field(default="INFO", description="Log level")

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024


settings = Settings()