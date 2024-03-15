import asyncio
import aiohttp
import pandas as pd
from io import StringIO

df = pd.read_csv("df.csv")


async def fetch_data(session, url, params):
    async with session.get(url, params=params) as response:
        return await response.text()


async def process_row(row, url):
    vars = {
        "zkratka": row["zkratka"],
        "katedra": row["katedra"],
        "lang": "en",
        "outputFormat": "CSV",
        "outputFormatEncoding": "utf-8",
    }
    async with aiohttp.ClientSession() as session:
        response_text = await fetch_data(session, url, params=vars)
        df_predmet = pd.read_csv(StringIO(response_text), sep=";")
        df_predmet.fillna("—", inplace=True)

        return df_predmet


async def main():
    url = "https://ws.ujep.cz/ws/services/rest2/predmety/getPredmetInfo"
    temp_dfs = []

    tasks = [process_row(row, url) for _, row in df.iterrows()]
    temp_dfs = await asyncio.gather(*tasks)

    predmety_df = pd.concat(temp_dfs)
    predmety_df.reset_index(inplace=True)
    predmety_df.to_csv("predmety.csv", index=False)


if __name__ == "__main__":
    asyncio.run(main())
