"""Připojení k Redis databázi.

https://stackoverflow.com/questions/73563804/what-is-the-recommended-way-to-instantiate-and-pass-around-a-redis-client-with-f
"""

import redis
from loguru import logger

pool = redis.ConnectionPool(host="redis", port=6379, db=0, decode_responses=True)


def get_redis() -> redis.Redis:
    """Vrátí instanci Redis klienta."""
    try:
        return redis.Redis(connection_pool=pool)
    except Exception as e:
        logger.error(e)
        return None
