from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / '.env',
        extra='ignore',
        hide_input_in_errors=True,
    )
    database_url: str = Field(description='Required PostgreSQL connection URL; no default')
    cors_origins: list[str] = [
        'http://localhost:5173',
        'http://127.0.0.1:5173',
        'http://localhost:63342',
        'http://127.0.0.1:63342',
    ]
    session_hours: int = Field(default=8, ge=1, le=720)
    login_limit: int = Field(default=10, ge=1, le=1000)
    login_window_seconds: int = Field(default=900, ge=1)

    environment: str = 'development'
    redis_url: str | None = 'redis://127.0.0.1:6379/0'
    user_jwt_secret: SecretStr | None = None
    user_jwt_issuer: str = 'ws-fastvue-user'
    user_refresh_token_days: int = Field(default=7, ge=7, le=30)
    user_auth_redis_prefix: str = 'fastvue:user:auth'
    user_sms_mock_enabled: bool = False
    sms_gateway_url: str | None = None
    sms_gateway_token: SecretStr | None = None

    @model_validator(mode='after')
    def production_sms_requires_verification(self):
        if self.environment.strip().lower() == 'production' and self.user_sms_mock_enabled:
            raise ValueError('USER_SMS_MOCK_ENABLED must be false in production')
        return self

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
