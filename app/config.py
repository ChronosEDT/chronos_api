import logging
from functools import lru_cache

from pydantic import AnyHttpUrl, HttpUrl, RedisDsn, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True)

    API_V1_STR: str = "/api/v1"

    PROJECT_NAME: str = "ChronosAPI"
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = []

    SENTRY_DSN: HttpUrl | None = None

    REDIS_DOMAIN: str
    REDIS_PORT: str
    REDIS_URI: RedisDsn | None = None

    EDT_CACHE_TIME: int = 15 * 60
    CHRONOS_GROUP_URL: AnyHttpUrl
    CHRONOS_EDT_URL: AnyHttpUrl

    LOG_LEVEL: int = logging.WARNING

    @field_validator("SENTRY_DSN", mode="before")
    @classmethod
    def sentry_dsn_can_be_blank(cls, v: str | None) -> str | None:
        if v is None or len(v) == 0:
            return None
        return v

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | list[str]) -> str | list[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list | str):  # pyright: ignore
            return v
        raise ValueError(v)

    @field_validator("REDIS_URI", mode="before")
    @classmethod
    def assemble_cachedb_connection(
        cls, v: str | None, info: ValidationInfo
    ) -> RedisDsn | str:
        if isinstance(v, str):
            return v
        return RedisDsn.build(
            scheme="redis",
            host=info.data.get("REDIS_DOMAIN", ""),
            port=info.data.get("REDIS_PORT", ""),
            path="/0",
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # pyright: ignore
