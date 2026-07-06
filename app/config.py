from __future__ import annotations

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    BOT_TOKEN: str
    DATABASE_URL: str

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def _force_asyncpg_driver(cls, value: str) -> str:
        if value.startswith("postgres://"):
            return "postgresql+asyncpg://" + value[len("postgres://"):]
        if value.startswith("postgresql://"):
            return "postgresql+asyncpg://" + value[len("postgresql://"):]
        return value

    ADMIN_ID_1: int | None = None
    ADMIN_ID_2: int | None = None
    ADMIN_ID_3: int | None = None

    @field_validator("ADMIN_ID_1", "ADMIN_ID_2", "ADMIN_ID_3", mode="before")
    @classmethod
    def _blank_to_none(cls, value):
        if value is None:
            return None
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @property
    def admin_ids(self) -> set[int]:
        return {
            admin_id
            for admin_id in (self.ADMIN_ID_1, self.ADMIN_ID_2, self.ADMIN_ID_3)
            if admin_id is not None
        }


settings = Settings()