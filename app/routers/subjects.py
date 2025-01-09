"""Routy pro jednotlivé stránky a komponenty."""

from typing import Annotated

import pandas as pd
from fastapi import APIRouter, Depends, Form, Path, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from loguru import logger
from redis import Redis

from app.redis_conn import get_redis
from app.settings import settings
from app.utils import filter_df, get_df, process_breaks, process_df
from app.validators import Faculty

router = APIRouter(prefix="/subjects", tags=["Subjects"])

templates = Jinja2Templates(directory="app/templates")

url = "https://ws.ujep.cz/ws/services/rest2/predmety/getPredmetyByFakultaFullInfo"
auth = settings.get_auth()

faculties = {
    "all": "All faculties",
    "fud": "Faculty of Art and Design",
    "ff": "Faculty of Arts",
    "fse": "Faculty of Social and Economic Studies",
    "fzp": "Faculty of Environment",
    "fzs": "Faculty of Health Studies",
    "pf": "Faculty of Education",
    "prf": "Faculty of Science",
    "fsi": "Faculty of Mechanical Engineering",
}


@router.get("")
def endpoint_get_subjects(
    request: Request,
    redis_client: Annotated[Redis, Depends(get_redis)],
    year: Annotated[str, Query(title="Year", description="Academic year")],
    faculty: Annotated[
        Faculty | None, Query(title="Faculty", description="Faculty code/All")
    ] = None,
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
                "faculties": faculties,
            },
        )

    except Exception as e:
        logger.error(e)
        return HTMLResponse(content="<h1>Error on our side</h1>", status_code=500)


@router.post("/{faculty}/{year}")
def endpoint_filter_df(
    request: Request,
    faculty: Faculty,
    redis_client: Annotated[Redis, Depends(get_redis)],
    year: Annotated[str, Path(title="Year", description="Academic year")],
    faculty_short: Annotated[str | None, Form(alias="Faculty")] = None,
    department: Annotated[str, Form(alias="Department")] = None,
    shortcut: Annotated[str, Form(alias="Code")] = None,
    name: Annotated[str, Form(alias="Name")] = None,
    winter: Annotated[bool, Form(alias="Winter term")] = None,
    summer: Annotated[bool, Form(alias="Summer term")] = None,
    credit: Annotated[str, Form(alias="Credits")] = None,
    languages: Annotated[str, Form(alias="Languages")] = None,
    level: Annotated[str, Form(alias="Level")] = None,
) -> HTMLResponse:
    """Slouží k filtrování tabulky s předměty podle zadaných parametrů."""
    logger.info(f"Filtering {faculty} {year} {faculty_short} {department} {shortcut} {name}")
    try:
        predmety_df = get_df(faculty, year, redis_client)
        df_filter = process_df(predmety_df)

        df_filter = filter_df(
            df_filter,
            faculty_short=faculty_short,
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
    request: Request,
    department: str,
    predmet_zkr: str,
    faculty: Faculty,
    year: str,
    redis_client: Annotated[Redis, Depends(get_redis)],
) -> HTMLResponse:
    """Detail předmětu."""
    try:
        predmety_df = get_df(faculty, year, redis_client)

        df_predmet = predmety_df.loc[
            (predmety_df["zkratka"] == predmet_zkr) & (predmety_df["katedra"] == department)
        ]

        df_predmet["anotace"] = df_predmet["anotace"].apply(process_breaks)
        df_predmet["prehledLatky"] = df_predmet["prehledLatky"].apply(process_breaks)
        df_predmet["pozadavky"] = df_predmet["pozadavky"].apply(process_breaks)

        return templates.TemplateResponse(
            "components/modal.html",
            {"request": request, "df": df_predmet, "faculties": faculties},
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
    redis_client: Annotated[Redis, Depends(get_redis)],
    request: Request,
    faculty: Faculty,
    search: str | None = None,
    year: str = None,
) -> HTMLResponse:
    """Vyhledávání předmětů."""
    if search:
        predmety_df = get_df(faculty, year, redis_client)

        df_facult = predmety_df.loc[
            (predmety_df["anotace"].str.contains(search, case=False, na=False))
            | (predmety_df["prehledLatky"].str.contains(search, case=False, na=False))
            | (predmety_df["nazevDlouhy"].str.contains(search, case=False, na=False))
            | (predmety_df["nazev"].str.contains(search, case=False, na=False))
        ]

        df_facult["anotace"] = df_facult["anotace"].apply(process_breaks)
        df_facult["prehledLatky"] = df_facult["prehledLatky"].apply(process_breaks)
        df_facult["pozadavky"] = df_facult["pozadavky"].apply(process_breaks)

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
            {
                "request": request,
                "df": df_facult,
                "search": search,
                "faculty": faculty,
                "faculties": faculties,
            },
        )

    return HTMLResponse(content='<div id="cards_content"></div>', status_code=200)
