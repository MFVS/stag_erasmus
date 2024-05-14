import pandas as pd
from loguru import logger


def process_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df[
        [
            "katedra",
            "zkratka",
            "nazev",
            "vyukaZS",
            "vyukaLS",
            "kreditu",
            "vyucovaciJazyky",
            "urovenNastavena",
        ]
    ]
    df.columns = [
        "Department",
        "Code",
        "Name",
        "Winter term",
        "Summer term",
        "Credits",
        "Languages",
        "Level",
    ]
    df.fillna("—", inplace=True)
    
    return df


def filter_df(
    df: pd.DataFrame,
    department: str = None,
    shortcut: str = None,
    name: str = None,
    winter: bool = None,
    summer: bool = None,
    credits: int = None,
    languages: str = None,
    level: str = None,
) -> pd.DataFrame:
    if department:
        df_filter = df_filter.loc[df_filter["Department"] == department]
    if shortcut:
        df_filter = df_filter[
            df_filter["Code"].str.contains(shortcut, case=False, na=False)
        ]
    if name:
        df_filter = df_filter[
            df_filter["Name"].str.contains(name, case=False, na=False)
        ]
    if winter:
        df_filter = df_filter[df_filter["Winter term"] == "A"]
    if summer:
        df_filter = df_filter[df_filter["Summer term"] == "A"]
    if credits:
        df_filter = df_filter[df_filter["Credits"] == credits]
    if languages:
        df_filter = df_filter[
            df_filter["Languages"].str.contains(languages, case=False, na=False)
        ]
    if level:
        df_filter = df_filter[df_filter["Level"] == level]

    df_filter.fillna("—", inplace=True)
    return df_filter
