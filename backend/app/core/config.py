from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / '.env', extra='ignore'
    )
    database_url: str = 'postgresql+asyncpg://fastvue:change-me@127.0.0.1:5432/fastvue'
    cors_origins: list[str] = ['http://localhost:5173', 'http://127.0.0.1:5173']
    session_hours: int = Field(default=8, ge=1, le=720)
    login_limit: int = Field(default=10, ge=1, le=1000)
    login_window_seconds: int = Field(default=900, ge=1)

    @field_validator('database_url')
    @classmethod
    def postgres_only(cls, value: str) -> str:
        if not value.startswith('postgresql+asyncpg://'):
            raise ValueError('DATABASE_URL must use postgresql+asyncpg://')
        return value

    @field_validator('cors_origins')
    @classmethod
    def explicit_origins(cls, value: list[str]) -> list[str]:
        if '*' in value:
            raise ValueError('CORS_ORIGINS must list explicit origins')
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
