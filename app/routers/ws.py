from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from io import StringIO, BytesIO
import requests
import pandas as pd
import aiohttp

from ..redis_db import redis_client

router = APIRouter(prefix="/ws", tags=["WS"])

templates = Jinja2Templates(directory="app/templates")

@router.get("/predmet/{predmet_zkr}/{katedra}")
def get_predmet(request: Request, predmet_zkr: str, katedra: str):

    if redis_client.exists(f"predmet:{predmet_zkr}"):
        predmet = redis_client.get(f"predmet:{predmet_zkr}")
        df = pd.read_json(BytesIO(predmet), orient="records")

    else:
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

    return templates.TemplateResponse(
        "components/modal.html", {"request": request, "df": df}
    )

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

@router.get("/cards")
async def get_cards(request: Request):
    predmety_df = pd.read_csv("predmety.csv")

    return templates.TemplateResponse(
        "components/cards.html", {"request": request, "df": predmety_df}
    )

@router.post("/filter")
def filter_df(
    request: Request,
    department: str = Form(alias="Department"),
    shortcut: str = Form(None, alias="Code"),
    name: str = Form(None, alias="Name"),
    winter: bool = Form(None, alias="Winter term"),
    summer: bool = Form(None, alias="Summer term"),
):

    df = pd.read_csv("df.csv")
    df_filter = df[["katedra", "zkratka", "nazev", "vyukaZS", "vyukaLS"]]
    df_filter.columns = ["Department", "Code", "Name", "Winter term", "Summer term"]

    if department == "All":
        department = None

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

    return templates.TemplateResponse(
        "components/table.html",
        {
            "request": request,
            "df_predmety": df_filter,
        },
    )