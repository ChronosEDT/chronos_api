from typing import cast

import redis
from pydantic import RedisDsn

from app.config import get_settings
from app.logger import get_logger

logger = get_logger(__name__)


def get_redis() -> redis.Redis[bytes] | None:
    settings = get_settings()
    try:
        redis_client = redis.Redis(
            host=cast(str, cast(RedisDsn, settings.REDIS_URI).host),
            port=int(cast(str, cast(RedisDsn, settings.REDIS_URI).port)),
            db=0,
            decode_responses=False,
        )

        if redis_client.ping():
            return redis_client

        logger.warning("Redis: ping failed!")
        return None
    except redis.exceptions.RedisError:
        logger.warning("Redis: An error ocurred while connecting")
        return None
