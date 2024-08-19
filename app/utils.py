"""Modul obsahující funkce pro předzpracování a filtrování DataFrame."""

import pandas as pd
from loguru import logger


def process_df(subjects_df: pd.DataFrame) -> pd.DataFrame:
    """Předzpracování DataFramu. Vybrání sloupců, přejmenování a doplnění chybějících hodnot.

    Args:
    ----
        subjects_df (pd.DataFrame): Původní DataFrame.

    Returns:
    -------
        pd.DataFrame: Předzpracovaný DataFrame.

    """
    logger.info(subjects_df.columns)

    processed_df = subjects_df[
        [
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
        "Department",
        "Code",
        "Name",
        "Winter term",
        "Summer term",
        "Credits",
        "Languages",
        "Level",
    ]

    processed_df.loc[:, "Languages"] = processed_df.loc[:, "Languages"].fillna("N/D")
    processed_df.loc[:, "Level"] = processed_df.loc[:, "Level"].fillna("N/D")

    return processed_df


def filter_df(
    df_filter: pd.DataFrame,
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
        df_filer (pd.DataFrame): Původní DataFrame.
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
    if department == "All":
        department = None
    credit = None if credit == "All" else int(credit)
    if languages == "All":
        languages = None
    if level == "All":
        level = None

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
