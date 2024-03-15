from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from .routers import subjects


app = FastAPI(
    # docs_url=None,
    redoc_url=None,
    title="FastAPI Template",
    description="A simple FastAPI template",
    version="0.1.0",
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("pages/home.html", {"request": request})


app.include_router(subjects.router)
