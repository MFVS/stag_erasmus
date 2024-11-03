"""Hlavní modul aplikace."""

import warnings
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi.responses import FileResponse, HTMLResponse
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from loguru import logger

from app.routers import subjects


@asynccontextmanager
async def lifespan(app: FastAPI) -> None:  # noqa: ARG001
    """Smazání dat při ukončení aplikace."""
    yield
    logger.info("DELETING DATA...")
    subjects.redis_client.flushdb()


app = FastAPI(
    docs_url=None,
    redoc_url=None,
    title="STAG ERASMUS",
    lifespan=lifespan,
)
warnings.simplefilter(action="ignore", category=FutureWarning)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")


@app.get("/")
async def root(request: Request, selected: bool = True) -> HTMLResponse:
    """Domovská stránka aplikace."""
    year_now = datetime.now().year
    years = list(range(year_now - 1, year_now + 2))

    return templates.TemplateResponse(
        "pages/home.html",
        {
            "request": request,
            "years": years,
            "modal_active": not selected,
            "current_year": year_now,
        },
    )


@app.get("/favicon.ico")
async def favicon() -> FileResponse:
    """Favicon."""
    return FileResponse("app/static/logos/ujep_stripes.svg")


app.include_router(subjects.router)
