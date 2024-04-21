from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, field_validator
import pandas as pd
# from loguru import logger
from io import StringIO, BytesIO
import requests
import redis

from ..utils import process_df, filter_df

router = APIRouter(prefix="/subjects", tags=["Subjects"])

templates = Jinja2Templates(directory="app/templates")

df = pd.read_csv("search_predmety.csv", delimiter=";")
df_predmety = pd.read_csv("predmety.csv")
redis_client = redis.Redis(host="redis", port=6379, db=0)


@router.get("/")
def get_subjects(faculty: str, year: str, request: Request):
    try:
        faculty = faculty.lower()
        new_df = df.loc[(df["fakulta"].str.lower() == faculty) & (df["rok"] == int(year))]
        df_facult = process_df(new_df)
        df_facult.fillna("–", inplace=True)
        unique_languages = df_facult["Languages"].str.split(", ").explode().unique().tolist()

        return templates.TemplateResponse(
            "pages/faculty.html",
            {"request": request, "faculty": faculty, "year": year, "df": df_facult, "unique_languages": unique_languages},
        )
    except Exception as e:
        logger.error(e)
        return HTMLResponse(content=f"<h1>Error on our side</h1>", status_code=500)


@router.post("/filter/{faculty}/{year}")
def filter_df(
    request: Request,
    faculty: str,
    year: str,
    department: str = Form(None, alias="Department"),
    shortcut: str = Form(None, alias="Code"),
    name: str = Form(None, alias="Name"),
    winter: bool = Form(None, alias="Winter term"),
    summer: bool = Form(None, alias="Summer term"),
    credits: str = Form(None, alias="Credits"),
    languages: str = Form(None, alias="Languages"),
    level: str = Form(None, alias="Level")
):
    faculta_df = df.loc[(df["fakulta"].str.lower() == faculty) & (df["rok"] == int(year))]
    df_filter = process_df(faculta_df)

    if department == "All":
        department = None
    if credits == "All":
        credits = None
    else:
        credits = int(credits)
    if languages == "All":
        languages = None
    if level == "All":
        level = None

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
    
    df_filter.fillna("–", inplace=True)

    return templates.TemplateResponse(
        "components/table.html",
        {
            "request": request,
            "df": df_filter,
            "year": year,
        },
    )


@router.get("/{predmet_zkr}/{katedra}/{year}")
def get_predmet(request: Request, predmet_zkr: str, katedra: str, year: str):
    url = "https://ws.ujep.cz/ws/services/rest2/predmety/getPredmetInfo"
    vars = {
        "zkratka": predmet_zkr,
        "katedra": katedra,
        "lang": "en",
        "outputFormat": "CSV",
        "outputFormatEncoding": "utf-8",
    }
    print(f"predmet:{predmet_zkr}:{year}")
    if redis_client.exists(f"predmet:{predmet_zkr}:{year}"):
        predmet = redis_client.get(f"predmet:{predmet_zkr}:{year}")
        df = pd.read_json(BytesIO(predmet), orient="records")

    else:
        url = "https://ws.ujep.cz/ws/services/rest2/predmety/getPredmetInfo"
        vars = {
            "zkratka": predmet_zkr,
            "katedra": katedra,
            "rok": year,
            "lang": "en",
            "outputFormat": "CSV",
            "outputFormatEncoding": "utf-8",
        }
        response = requests.get(url, params=vars)

        df = pd.read_csv(StringIO(response.text), sep=";")
        df.fillna("–", inplace=True)

        redis_client.setex(f"predmet:{predmet_zkr}:{year}", 60, df.to_json())

    df = pd.read_csv(StringIO(requests.get(url, params=vars).text), sep=";")
    df.fillna("–", inplace=True)

    return templates.TemplateResponse(
        "components/modal.html", {"request": request, "df": df}
    )


@router.get("/cards")
def get_cards(request: Request, search: str = None):
    if search:
        df_search_predmety = df_predmety.loc[
            (df_predmety["anotace"].str.contains(search, case=False, na=False)) | (df_predmety["prehledLatky"].str.contains(search, case=False, na=False))
        ]

    return templates.TemplateResponse("components/cards.html", {"request": request, "df": df_search_predmety})