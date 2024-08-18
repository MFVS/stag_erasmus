import pandas as pd


def process_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df[
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
    df.is_copy = False

    # FIXME: pokud ma sloupec Level jen nan tak tak se logguje incompatible dtype chyba
    df.loc[:, "Languages"] = df.loc[:, "Languages"].fillna("N/D")
    df.loc[:, "Level"] = df.loc[:, "Level"].fillna("N/D")

    return df


def filter_df(
    df: pd.DataFrame,
    department: str = None,
    shortcut: str = None,
    name: str = None,
    winter: bool = None,
    summer: bool = None,
    credit: int = None,
    languages: str = None,
    level: str = None,
) -> pd.DataFrame:
    df_filter = df.copy()
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
