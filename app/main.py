from fastapi import FastAPI, Request, status
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, JSONResponse, FileResponse
from fastapi.exceptions import RequestValidationError
import logging
import os

from .routers import ws
from .utils import get_df

app = FastAPI(
    docs_url="/docs",
    redoc_url=None,
    title="STAG API",
)

templates = Jinja2Templates(directory="app/templates")
app.mount("/static/*", StaticFiles(directory="app/static"), name="static")


app = FastAPI()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc_str = f"{exc}".replace("\n", " ").replace("   ", " ")
    logging.error(f"{request}: {exc_str}")
    content = {"status_code": 10422, "message": exc_str, "data": None}
    return JSONResponse(
        content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )


@app.get("/")
def login(request: Request, stagUserTicket: str | None = None):
    if stagUserTicket and stagUserTicket != b"anonymous" and stagUserTicket != b"None":
        return RedirectResponse(url=f"/home?stagUserTicket={stagUserTicket}" )
    else:
        login_url = "https://ws.ujep.cz/ws/login?originalURL=http://localhost:8000"
        return RedirectResponse(url=login_url)


@app.get("/home")
async def home(request: Request, stagUserTicket: str):
    url = "https://ws.ujep.cz/ws/services/rest2/predmety/getPredmetyByFakulta"
    params = {
        "fakulta": "PRF",
        "lang": "en",
        "outputFormat": "CSV",
        "outputFormatEncoding": "utf-8",
        "jenNabizeneECTSPrijezdy": "true",
        "rok": "2023",
    }

    df_predmety = get_df(url, params, ticket=stagUserTicket)
    df_predmety = df_predmety[["katedra", "zkratka", "nazev", "vyukaZS", "vyukaLS"]]
    df_predmety.columns = ["Department", "Code", "Name", "Winter term", "Summer term"]
    df_predmety_str = df_predmety.to_json(orient="records")

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "df_predmety": df_predmety,
            "df_predmety_str": df_predmety_str,
        },
    )


@app.get("/static/{image}")
async def image(image: str):
    return FileResponse(f"app/static/{image}", media_type="image/svg+xml")


app.include_router(ws.router)
