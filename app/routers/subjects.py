from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, field_validator
import pandas as pd
from io import StringIO, BytesIO
import requests
import redis

router = APIRouter(prefix="/subjects", tags=["Subjects"])

templates = Jinja2Templates(directory="app/templates")

df = pd.read_csv("df.csv", delimiter=";")
redis_client = redis.Redis(host="redis", port=6379, db=0)


@router.get("/")
def get_subjects(faculty: str, year: str, request: Request):
    try:
        
        df_facult = df[["katedra", "zkratka", "nazev", "vyukaZS", "vyukaLS", "kreditu", "vyucovaciJazyky", "urovenNastavena"]]
        df_facult.columns = ["Department", "Code", "Name", "Winter term", "Summer term", "Credits", "Languages", "Level"]

        return templates.TemplateResponse(
            "pages/faculty.html",
            {"request": request, "faculty": faculty, "year": year, "df": df_facult},
        )
    except Exception as e:
        return HTMLResponse(content=f"<h1>Error on our side</h1>", status_code=500)


@router.post("/filter")
def filter_df(
    request: Request,
    department: str = Form(None, alias="Department"),
    shortcut: str = Form(None, alias="Code"),
    name: str = Form(None, alias="Name"),
    winter: bool = Form(None, alias="Winter term"),
    summer: bool = Form(None, alias="Summer term"),
    credits: str = Form(None, alias="Credits"),
    languages: str = Form(None, alias="Languages"),
    level: str = Form(None, alias="Level")
):
    
    df_filter = df[["katedra", "zkratka", "nazev", "vyukaZS", "vyukaLS", "kreditu", "vyucovaciJazyky", "urovenNastavena"]]
    df_filter.columns = ["Department", "Code", "Name", "Winter term", "Summer term", "Credits", "Languages", "Level"]
    
    if department == "All":
        department = None
    if credits == "-":
        credits = None
    else:
        credits = int(credits)
    if languages == "All":
        languages = None
    if level == "All":
        level = None
        
    print(department, shortcut, name, winter, summer, credits, languages, level)
    print(df_filter["Credits"].unique())
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
    
    return templates.TemplateResponse(
        "components/table.html",
        {
            "request": request,
            "df": df_filter,
        },
    )


@router.get("/{predmet_zkr}/{katedra}")
def get_predmet(request: Request, predmet_zkr: str, katedra: str):
    url = "https://ws.ujep.cz/ws/services/rest2/predmety/getPredmetInfo"
    vars = {
        "zkratka": predmet_zkr,
        "katedra": katedra,
        "lang": "en",
        "outputFormat": "CSV",
        "outputFormatEncoding": "utf-8",
    }

    if redis_client.exists(f"predmet:{predmet_zkr}"):
        print("uz tam byl")
        predmet = redis_client.get(f"predmet:{predmet_zkr}")
        df = pd.read_json(BytesIO(predmet), orient="records")

    else:
        print("nebyl tam")
        url = "https://ws.ujep.cz/ws/services/rest2/predmety/getPredmetInfo"
        vars = {
            "zkratka": predmet_zkr,
            "katedra": katedra,
            "lang": "en",
            "outputFormat": "CSV",
            "outputFormatEncoding": "utf-8",
        }

        df = pd.read_csv(StringIO(requests.get(url, params=vars).text), sep=";")
        df.fillna("—", inplace=True)

        redis_client.setex(f"predmet:{predmet_zkr}", 60, df.to_json())

    df = pd.read_csv(StringIO(requests.get(url, params=vars).text), sep=";")
    df.fillna("—", inplace=True)
    # print(df.columns)
    # print(df[["jednotekPrednasek","jednotkaPrednasky"]])
    return templates.TemplateResponse(
        "components/modal.html", {"request": request, "df": df}
    )