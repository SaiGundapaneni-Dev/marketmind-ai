from __future__ import annotations

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):
    app_name: str = "MarketMind AI"
    app_version: str = "1.0.0"
    environment: str = "development"

    database_url: str

    jwt_secret_key: str = Field(
        min_length=32,
    )
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # Keep this as a plain string so pydantic-settings
    # does not try to JSON-decode it.
    cors_origins: str = (
        "http://localhost:3000,"
        "http://127.0.0.1:3000"
    )

    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    @field_validator(
        "database_url",
        mode="before",
    )
    @classmethod
    def normalize_database_url(
        cls,
        value: str,
    ) -> str:
        value = value.strip()

        if value.startswith("postgres://"):
            return value.replace(
                "postgres://",
                "postgresql://",
                1,
            )

        return value

    @property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip().rstrip("/")
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]

    @property
    def is_production(self) -> bool:
        return (
            self.environment.lower()
            == "production"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()