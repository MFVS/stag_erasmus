from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from datetime import datetime
import warnings

from .routers import subjects


app = FastAPI(
    docs_url=None,
    redoc_url=None,
    title="STAG ERASMUS",
    version="0.1.0",
)
warnings.simplefilter(action='ignore', category=FutureWarning)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")


@app.get("/")
async def root(request: Request):
    YEAR_NOW = datetime.now().year
    years = [year for year in range(YEAR_NOW - 1, YEAR_NOW + 2)]
    
    return templates.TemplateResponse("pages/home.html", {"request": request, "years": years})


app.include_router(subjects.router)
