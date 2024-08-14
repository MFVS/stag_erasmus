"""Skript pro stahování dat z API STAGu a ukládání do Redisu."""

import datetime
import os
import time

import redis
import requests
import schedule
from dotenv import load_dotenv
from loguru import logger
from tqdm import tqdm

load_dotenv()

redis_client = redis.Redis(host="redis", port=6379, db=0)
NOW = datetime.datetime.now()
url = "https://ws.ujep.cz/ws/services/rest2/predmety/getPredmetyByFakultaFullInfo"
auth = (os.getenv("STAG_USER"), os.getenv("STAG_PASSWORD"))
params = {
    "lang": "en",
    "jenNabizeneECTSPrijezdy": "true",
    "outputFormat": "JSON",
    "outputFormatEncoding": "utf-8",
}

faculties = ["FSI", "FF", "PRF", "FZP", "FZS", "PF", "FSE", "FUD"]
years = list(range(NOW.year - 1, NOW.year + 2))


def download_data() -> None:
    """Download data from STAG API and cache them in Redis."""
    logger.info("DOWNLOADING DATA...")
    for faculty in tqdm(faculties):
        params["fakulta"] = faculty
        logger.info(f"{faculty}")
        for year in years:
            params["rok"] = year
            response = requests.get(url, params=params, auth=auth, timeout=10)
            if not response.ok:
                logger.error(f"Error downloading data for {faculty} - {year}")
                continue
            redis_client.setex(f"predmety:{faculty}:{year}", 84600, response.text)  # 84600s = 23.5h
    logger.info("DATA CACHED SUCCESSFULLY!")


schedule.every().day.at("00:30").do(download_data)

while True:
    schedule.run_pending()
    time.sleep(1)
