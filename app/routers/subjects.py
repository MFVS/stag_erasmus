"""Routy pro jednotlivé stránky a komponenty."""

import os

import pandas as pd
import redis
from dotenv import load_dotenv
from fastapi import APIRouter, Form, Path, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from loguru import logger

from app.utils import filter_df, get_df, process_df
from app.validators import Faculty

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
def endpoint_get_subjects(
    request: Request,
    faculty: Faculty | None = Query(default=None, title="Faculty", description="Faculty code/All"),
    year: str = Query(title="Year", description="Academic year"),
) -> HTMLResponse:
    """Stránka fakulty s předměty."""
    if faculty is None:
        return RedirectResponse(url="/?selected=false", status_code=302)
    try:
        predmety_df = get_df(faculty, year, redis_client)

        if predmety_df.empty:
            df_facult = pd.DataFrame()
            unique_languages = []
        else:
            df_facult = process_df(predmety_df)
            unique_languages = df_facult["Languages"].str.split(", ").explode().unique().tolist()

        return templates.TemplateResponse(
            "pages/faculty.html",
            {
                "request": request,
                "faculty": faculty.value,
                "year": year,
                "df": df_facult,
                "unique_languages": unique_languages,
                "faculty_name": faculties[faculty.name]
                if faculty != Faculty.all
                else "All faculties",
            },
        )

    except Exception as e:
        logger.error(e)
        return HTMLResponse(content="<h1>Error on our side</h1>", status_code=500)


@router.post("/{faculty}/{year}")
def endpoint_filter_df(
    request: Request,
    faculty: Faculty,
    year: str = Path(title="Year", description="Academic year"),
    department: str = Form(None, alias="Department"),
    shortcut: str = Form(None, alias="Code"),
    name: str = Form(None, alias="Name"),
    winter: bool = Form(None, alias="Winter term"),
    summer: bool = Form(None, alias="Summer term"),
    credit: str = Form(None, alias="Credits"),
    languages: str = Form(None, alias="Languages"),
    level: str = Form(None, alias="Level"),
) -> HTMLResponse:
    """Slouží k filtrování tabulky s předměty podle zadaných parametrů."""
    try:
        predmety_df = get_df(faculty, year, redis_client)
        df_filter = process_df(predmety_df)

        df_filter = filter_df(
            df_filter,
            department=department,
            shortcut=shortcut,
            name=name,
            winter=winter,
            summer=summer,
            credit=credit,
            languages=languages,
            level=level,
        )

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
        return HTMLResponse(content="<h1>Error on our side</h1>", status_code=500)


@router.get("/predmet/{department}/{predmet_zkr}/{faculty}/{year}")
def endpoint_get_predmet(
    request: Request, department: str, predmet_zkr: str, faculty: Faculty, year: str
) -> HTMLResponse:
    """Detail předmětu."""
    try:
        predmety_df = get_df(faculty, year, redis_client)

        df_predmet = predmety_df.loc[
            (predmety_df["zkratka"] == predmet_zkr) & (predmety_df["katedra"] == department)
        ]

        return templates.TemplateResponse(
            "components/modal.html",
            {"request": request, "df": df_predmet},
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
def endpoint_get_cards(
    request: Request, faculty: Faculty, search: str | None = None, year: str = None
) -> HTMLResponse:
    """Vyhledávání předmětů."""
    if search:
        predmety_df = get_df(faculty, year, redis_client)

        df_facult = predmety_df.loc[
            (predmety_df["anotace"].str.contains(search, case=False, na=False))
            | (predmety_df["prehledLatky"].str.contains(search, case=False, na=False))
            | (predmety_df["nazevDlouhy"].str.contains(search, case=False, na=False))
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

    return HTMLResponse(content='<div id="cards_content"></div>', status_code=200)
