"""Hlavní modul aplikace."""

import warnings
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from loguru import logger

from app.routers import subjects


@asynccontextmanager
async def lifespan(app: FastAPI) -> None:
    """Stahování dat při spuštění aplikace a jejich smazání při ukončení."""
    yield
    logger.info("DELETING DATA...")
    subjects.redis_client.flushdb()


app = FastAPI(
    docs_url="/docs",
    redoc_url=None,
    title="STAG ERASMUS",
    # version=importlib.metadata.version("stag-erasmus"),
    lifespan=lifespan,
)
warnings.simplefilter(action="ignore", category=FutureWarning)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")


@app.get("/")
async def root(request: Request) -> HTMLResponse:
    """Domovská stránka aplikace."""
    year_now = datetime.now().year
    years = list(range(year_now - 1, year_now + 2))

    return templates.TemplateResponse(
        "pages/home.html", {"request": request, "years": years, "modal_active": False}
    )


app.include_router(subjects.router)
