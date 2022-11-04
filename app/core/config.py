import logging
from functools import lru_cache
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, BaseSettings, HttpUrl, RedisDsn, validator


class Settings(BaseSettings, case_sensitive=True):
    API_V1_STR: str = "/api/v1"

    PROJECT_NAME: str = "EDTVelizy"
    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    SENTRY_DSN: Optional[HttpUrl] = None

    REDIS_DOMAIN: str
    REDIS_PORT: str
    REDIS_URI: Optional[RedisDsn] = None

    EDT_CACHE_TIME: int = 15 * 60
    CHRONOS_GROUP_URL: AnyHttpUrl
    CHRONOS_EDT_URL: AnyHttpUrl

    LOG_LEVEL: int = logging.WARNING

    @validator("SENTRY_DSN", pre=True)
    def sentry_dsn_can_be_blank(cls, v: Optional[str]) -> Optional[str]:
        if v is None or len(v) == 0:
            return None
        return v

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):  # pyright: ignore
            return v
        raise ValueError(v)

    @validator("REDIS_URI", pre=True)
    def assemble_cachedb_connection(
        cls, v: Optional[str], values: Dict[str, Any]
    ) -> Any:
        if isinstance(v, str):
            return v
        return RedisDsn.build(
            scheme="redis",
            host=values.get("REDIS_DOMAIN"),  # pyright: ignore
            port=values.get("REDIS_PORT"),
            path="/0",
        )


@lru_cache()
def get_settings() -> Settings:
    return Settings()  # pyright: ignore
