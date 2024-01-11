from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from io import StringIO
from unidecode import unidecode
import requests
import pandas as pd

router = APIRouter(prefix="/ws", tags=["WS"])

templates = Jinja2Templates(directory="app/templates")

@router.get("/predmet/{predmet_zkr}/{katedra}")
def get_predmet(request: Request, predmet_zkr: str, katedra: str):
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
    # print(df.columns)
    # print(df[["jednotekPrednasek","jednotkaPrednasky"]])
    return templates.TemplateResponse(
        "components/modal.html", {"request": request, "df": df}
    )


@router.post("/filter")
def filter_df(
    request: Request,
    df: str = Form(alias="df"),
    department: str = Form(alias="Department"),
    shortcut: str = Form(None, alias="Code"),
    name: str = Form(None, alias="Name"),
    winter: bool = Form(None, alias="Winter term"),
    summer: bool = Form(None, alias="Summer term"),
):
    
    df_filter = pd.read_json(StringIO(df))
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
            "df_predmety_str": df,
            "df_predmety_full": pd.read_json(StringIO(df)),
        },
    )