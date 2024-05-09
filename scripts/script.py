from loguru import logger
import datetime
import requests

import redis

redis_client = redis.Redis(host="redis", port=6379, db=0)
NOW = datetime.datetime.now()
url = ""


faculties = ["FSI", "FF", "PRF", "FŽP", "FZS", "PF", "FSE", "FUD"]
years = [year for year in range(2021, NOW.year + 1)]

logger.info("Hello, World!")
