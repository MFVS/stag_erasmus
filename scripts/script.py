from loguru import logger
import redis

redis_client = redis.Redis(host="redis", port=6379, db=0)

logger.info("Hello, World!")
