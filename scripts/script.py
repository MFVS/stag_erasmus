"""Skript pro stahování dat z API STAGu a ukládání do Redisu."""

import datetime
import os
import time
from io import StringIO

import pandas as pd
import redis
import requests
import schedule
from dotenv import load_dotenv
from loguru import logger
from tqdm import tqdm

load_dotenv()

redis_client = redis.Redis(host="redis", port=6379, db=0)
url = "https://ws.ujep.cz/ws/services/rest2/predmety/getPredmetyByFakultaFullInfo"
auth = (os.getenv("STAG_USER"), os.getenv("STAG_PASSWORD"))
params = {
    "lang": "en",
    "jenNabizeneECTSPrijezdy": "true",
    "outputFormat": "CSV",
    "outputFormatEncoding": "utf-8",
}
faculties = ["FSI", "FF", "PRF", "FZP", "FZS", "PF", "FSE", "FUD"]


def download_data() -> None:
    """Download data from STAG API and cache them in Redis."""
    now = datetime.datetime.now()
    years = list(range(now.year - 1, now.year + 2))

    logger.info("DOWNLOADING DATA...")
    for faculty in tqdm(faculties):
        params["fakulta"] = faculty
        logger.info(f"{faculty}")
        for year in years:
            params["rok"] = year
            response = requests.get(url, params=params, auth=auth)
            if not response.ok:
                logger.error(f"Error downloading data for {faculty} - {year}")
                continue
            data = pd.read_csv(StringIO(response.text), sep=";")
            redis_client.setex(f"predmety:{faculty.lower()}:{year}", 84600, data.to_json())
            # 84600s = 23.5h
    logger.info("DATA CACHED SUCCESSFULLY!")


if __name__ == "__main__":
    download_data()
    schedule.every().day.at("00:30").do(download_data)

    while True:
        schedule.run_pending()
        time.sleep(1)
