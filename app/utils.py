import httpx
from io import StringIO
import pandas as pd


def get_df(url: str, vars: dict, ticket: str) -> pd.DataFrame:
    request = httpx.Client().get(
        url,
        params=vars,
        cookies={"WSCOOKIE" : ticket},
    )
    response = request
    df = pd.read_csv(StringIO(response.text), sep=";")
    if df.empty:
        return None

    return df
