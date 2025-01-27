"""Modul obsahující funkce pro předzpracování a filtrování DataFrame."""

from io import StringIO

import pandas as pd
import requests
from loguru import logger
from redis import Redis

from app.settings import settings
from app.validators import Faculty

params = {
    "lang": "en",
    "jenNabizeneECTSPrijezdy": "true",
    "outputFormat": "CSV",
    "outputFormatEncoding": "utf-8",
}
url = "https://ws.ujep.cz/ws/services/rest2/predmety/getPredmetyByFakultaFullInfo"
auth = settings.get_auth()


def get_df(
    faculty: Faculty,
    year: int,
    redis_client: Redis,
) -> pd.DataFrame:
    """Pokud jsou data v Redisu, načtou se odtud. Jinak se stáhnou z API STAGu a uloží do Redisu.

    Args:
    ----
        faculty (Faculty): Enum fakulty.
        year (int): Rok.
        redis_client (Redis): Redis klient.

    """
    if faculty == Faculty.all:
        all_df = pd.DataFrame()
        for fac in Faculty:
            if fac == Faculty.all:
                continue
            predmety_df = get_df(fac, year, redis_client)

            all_df = pd.concat([all_df, predmety_df], ignore_index=True)

        return all_df

    params["fakulta"] = "FŽP" if faculty == Faculty.fzp else faculty.value.upper()
    params["rok"] = year
    if redis_client.exists(f"predmety:{faculty.value}:{year}"):
        logger.info(f"Data from Redis | {faculty.value} | {year}")
        predmety_faculty = redis_client.get(f"predmety:{faculty.value}:{year}")
        predmety_df = pd.read_json(StringIO(predmety_faculty), orient="records")
    else:
        logger.info(f"Data from WS | {faculty.value} | {year}")
        response = requests.get(url, params=params, auth=auth)
        predmety_df = pd.read_csv(StringIO(response.text), sep=";")
        redis_client.setex(f"predmety:{faculty.value}:{year}", 86400, predmety_df.to_json())
        # 24 hours

    return predmety_df.replace(
        {
            "DNU/SEM": "DAYS/TERM",
            "HOD/SEM": "HOURS/TERM",
            "HOD/TYD": "HOURS/WEEK",
            "TYD/SEM": "WEEKS/TERM",
        }
    )


def process_df(subjects_df: pd.DataFrame) -> pd.DataFrame:
    """Předzpracování DataFramu. Vybrání sloupců, přejmenování a doplnění chybějících hodnot.

    Args:
    ----
        subjects_df (pd.DataFrame): Původní DataFrame.

    Returns:
    -------
        pd.DataFrame: Předzpracovaný DataFrame.

    """
    processed_df = subjects_df[
        [
            "fakulta",
            "katedra",
            "zkratka",
            "nazevDlouhy",
            "vyukaZS",
            "vyukaLS",
            "kreditu",
            "vyucovaciJazyky",
            "urovenNastavena",
        ]
    ]
    processed_df.columns = [
        "Faculty",
        "Department",
        "Code",
        "Name",
        "Winter term",
        "Summer term",
        "Credits",
        "Languages",
        "Level",
    ]
    process_df.is_copy = False

    processed_df.loc[:, "Languages"] = processed_df.loc[:, "Languages"].fillna("N/D")
    processed_df.loc[:, "Level"] = processed_df.loc[:, "Level"].fillna("N/D")

    return processed_df


def filter_df(  # noqa: C901, PLR0912
    df_filter: pd.DataFrame,
    faculty_short: str | None = None,
    department: str = None,
    shortcut: str = None,
    name: str = None,
    winter: bool = None,
    summer: bool = None,
    credit: int = None,
    languages: str = None,
    level: str = None,
) -> pd.DataFrame:
    """Filtrace jednotlivých sloupců podle zadaných parametrů.

    Args:
    ----
        df_filter (pd.DataFrame): Původní DataFrame.
        faculty_short (str, optional): Zkratka fakulty. Defaults to None.
        department (str, optional): Katedra. Defaults to None.
        shortcut (str, optional): Zkratka předmětu. Defaults to None.
        name (str, optional): Název předmětu. Defaults to None.
        winter (bool, optional): Je vypisován v zimním semestru. Defaults to None.
        summer (bool, optional): Je vypisován v letním semestru. Defaults to None.
        credit (int, optional): Počet kreditů. Defaults to None.
        languages (str, optional): Jazyk výuky. Defaults to None.
        level (str, optional): Nastavená úroveň předmětu. Defaults to None.

    Returns:
    -------
        pd.DataFrame: Vyfiltrovaný DataFrame.

    """
    if faculty_short == "All":
        faculty_short = None
    if department == "All":
        department = None
    credit = None if credit == "All" else int(credit)
    if languages == "All":
        languages = None
    if level == "All":
        level = None

    if faculty_short:
        df_filter = df_filter.loc[df_filter["Faculty"] == faculty_short]
    if department:
        df_filter = df_filter.loc[df_filter["Department"] == department]
    if shortcut:
        df_filter = df_filter[df_filter["Code"].str.contains(shortcut, case=False, na=False)]
    if name:
        df_filter = df_filter[df_filter["Name"].str.contains(name, case=False, na=False)]
    if winter:
        df_filter = df_filter[df_filter["Winter term"] == "A"]
    if summer:
        df_filter = df_filter[df_filter["Summer term"] == "A"]
    if credit:
        df_filter = df_filter[df_filter["Credits"] == credit]
    if languages:
        df_filter = df_filter[df_filter["Languages"].str.contains(languages, case=False, na=False)]
    if level:
        df_filter = df_filter[df_filter["Level"] == level]

    return df_filter.fillna("N/D")


def process_breaks(string: str) -> str:
    """Převede znaky pro nový řádek na HTML tag <br>.

    Pouze pokuď se nejedná o HTML tagy.
    """
    if not pd.Series(string).str.contains("<[^<]+?>", regex=True).any() and string:
        return string.replace("\n", "<br>")
    return string
