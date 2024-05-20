from fastapi import APIRouter, Request, Form, Query, Path
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
import pandas as pd
from loguru import logger
from io import StringIO, BytesIO
from dotenv import load_dotenv
import requests
import redis
import os

from ..utils import process_df, filter_df
from ..validators import Faculty

router = APIRouter(prefix="/subjects", tags=["Subjects"])

templates = Jinja2Templates(directory="app/templates")

load_dotenv()

redis_client = redis.Redis(host="redis", port=6379, db=0)
url = "https://ws.ujep.cz/ws/services/rest2/predmety/getPredmetyByFakultaFullInfo"
auth = (os.getenv("STAG_USER"), os.getenv("STAG_PASSWORD"))

faculties = {
    "fsi": "Faculty of Mechanical Engineering",
    "ff": "Faculty of Arts",
    "prf": "Faculty of Science",
    "fžp": "Faculty of Environment",
    "fzs": "Faculty of Health Studies",
    "pf": "Faculty of Education",
    "fse": "Faculty of Social and Economic Studies",
    "fud": "Faculty of Art and Design",
}

@router.get("")
def get_subjects(
    request: Request,
    faculty: Faculty = Query(title="Faculty", description="Faculty code"),
    year: str = Query(title="Year", description="Academic year"),
    ):
    """
    Stránka fakulty s předměty.
    """
    params = {
        "fakulta": faculty.value.upper(),
        "lang": "en",
        "jenNabizeneECTSPrijezdy": "true",
        "rok": year,
        "outputFormat": "CSV",
        "outputFormatEncoding": "utf-8",
    }
    try:
        if redis_client.exists(f"predmety:{faculty.value}:{year}"):
            predmety_faculty = redis_client.get(f"predmety:{faculty.value}:{year}")
            df = pd.read_json(BytesIO(predmety_faculty), orient="records")
        else:
            response = requests.get(url, params=params, auth=auth)
            df = pd.read_csv(StringIO(response.text), sep=";")
            redis_client.setex(
                f"predmety:{faculty.value}:{year}", 86400, df.to_json()
            )  # 24 hours

        if df.empty:
            df_facult = pd.DataFrame()
            unique_languages = []
        else:
            df_facult = process_df(df)
            
            unique_languages = (
                df_facult["Languages"].str.split(", ").explode().unique().tolist()
            )

        return templates.TemplateResponse(
            "pages/faculty.html",
            {
                "request": request,
                    "faculty": faculty.value,
                    "year": year,
                    "df": df_facult,
                    "unique_languages": unique_languages,
                    "faculty_name": faculties[faculty.value],
                },
            )
        
            
    except Exception as e:
        logger.error(e)
        return HTMLResponse(content=f"<h1>Error on our side</h1>", status_code=500)


@router.post("/{faculty}/{year}")
def filter_df(
    request: Request,
    faculty: Faculty = Path(title="Faculty", description="Faculty code"),
    year: str = Path(title="Year", description="Academic year"),
    department: str = Form(None, alias="Department"),
    shortcut: str = Form(None, alias="Code"),
    name: str = Form(None, alias="Name"),
    winter: bool = Form(None, alias="Winter term"),
    summer: bool = Form(None, alias="Summer term"),
    credits: str = Form(None, alias="Credits"),
    languages: str = Form(None, alias="Languages"),
    level: str = Form(None, alias="Level"),
):
    """
    Slouží k filtrování tabulky s předměty podle zadaných parametrů.
    """
    params = {
        "fakulta": faculty.value.upper(),
        "lang": "en",
        "jenNabizeneECTSPrijezdy": "true",
        "rok": year,
        "outputFormat": "CSV",
        "outputFormatEncoding": "utf-8",
    }
    try:
        if redis_client.exists(f"predmety:{faculty.value}:{year}"):
            predmety_faculty = redis_client.get(f"predmety:{faculty.value}:{year}")
            df = pd.read_json(BytesIO(predmety_faculty), orient="records")
        else:
            response = requests.get(url, params=params, auth=auth)
            df = pd.read_csv(StringIO(response.text), sep=";")
            redis_client.setex(
                f"predmety:{faculty.value}:{year}", 86400, df.to_json()
            )  # 24 hours

        df_filter = process_df(df)

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

        return templates.TemplateResponse(
            "components/table.html",
            {
                "request": request,
                "df": df_filter,
                "year": year,
                "faculty": faculty.value,
            },
        )
    except Exception as e:
        logger.error(e)
        return HTMLResponse(content=f"<h1>Error on our side</h1>", status_code=500)


@router.get("/{predmet_zkr}/{faculty}/{year}")
def get_predmet(request: Request, predmet_zkr: str, faculty: Faculty, year: str):
    try:
        if redis_client.exists(f"predmety:{faculty}:{year}"):
            predmet = redis_client.get(f"predmety:{faculty}:{year}")
            df = pd.read_json(BytesIO(predmet), orient="records")
            df.fillna("–", inplace=True)

        else:
            params = {
                "fakulta": faculty.value.upper(),
                "lang": "en",
                "jenNabizeneECTSPrijezdy": "true",
                "rok": year,
                "outputFormat": "CSV",
                "outputFormatEncoding": "utf-8",
            }
            response = requests.get(url, params=params, auth=auth)

            df = pd.read_csv(StringIO(response.text), sep=";")
            df.fillna("–", inplace=True)

            redis_client.setex(f"predmet:{predmet_zkr}:{year}", 60, df.to_json())

        df_predmet = df.loc[df["zkratka"] == predmet_zkr]
        
        return templates.TemplateResponse(
            "components/modal.html", {"request": request, "df": df_predmet}
        )
    except Exception as e:
        modal = """
        <div id="modal" class="modal is-active"
            style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; overflow: auto;">
            <div class="modal-background" _="on click remove #modal"></div>
            <div class="modal-content has-text-white">
            <h1>Error on our side</h1>
            </div>
        </div>    
        """
        logger.error(e)
        return HTMLResponse(content=modal, status_code=500)


@router.get("/search/cards/{faculty}/{year}")
def get_cards(
    request: Request, faculty: str, search: str | None = None, year: str = None
):
    if search:
        if redis_client.exists(f"predmety:{faculty}:{year}"):
            predmety_faculty = redis_client.get(f"predmety:{faculty}:{year}")
            df = pd.read_json(BytesIO(predmety_faculty), orient="records")
        else:
            params = {
                "fakulta": faculty.upper(),
                "lang": "en",
                "jenNabizeneECTSPrijezdy": "true",
                "rok": year,
                "outputFormat": "CSV",
                "outputFormatEncoding": "utf-8",
            }
            response = requests.get(url, params=params, auth=auth)
            df = pd.read_csv(StringIO(response.text), sep=";")
            redis_client.setex(f"predmety:{faculty}", 86400, df.to_json())  # 24 hours

        df_facult = df.loc[
            (df["anotace"].str.contains(search, case=False, na=False))
            | (df["prehledLatky"].str.contains(search, case=False, na=False))
        ]

        if df_facult.empty:
            message = f"""
            <article id="cards_content" class="message is-warning is-medium">
                <div class="message-body">
                    No subjects found for <strong>{search}</strong>. Try searching for something else.
                </div>
            </article>"""
            return HTMLResponse(content=message, status_code=200)

        return templates.TemplateResponse(
            "components/cards.html",
            {"request": request, "df": df_facult, "search": search, "faculty": faculty},
        )
    else:
        return HTMLResponse(content='<div id="cards_content"></div>', status_code=200)
