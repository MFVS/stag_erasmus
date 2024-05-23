from loguru import logger
from tqdm import tqdm
from dotenv import load_dotenv
import os
import datetime
import requests
import redis
import schedule
import time

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
years = [year for year in range(NOW.year - 1, NOW.year + 2)]

def download_data():
    logger.info("DOWNLOADING DATA...")
    for faculty in tqdm(faculties):
        params["fakulta"] = faculty
        logger.info(f"{faculty}")
        for year in years:
            params["rok"] = year
            response = requests.get(url, params=params, auth=auth)
            if response.status_code != 200:
                logger.error(f"Error downloading data for {faculty} - {year}")
                continue
            redis_client.setex(
                f"predmety:{faculty}:{year}", 84600, response.text
            )  # 84600s = 23.5h
    logger.info("DATA CACHED SUCCESSFULLY!")

schedule.every().day.at("00:30").do(download_data)

while True:
    schedule.run_pending()
    time.sleep(1)
