from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import pandas as pd

router = APIRouter(prefix="/subjects", tags=["Subjects"])

templates = Jinja2Templates(directory="app/templates")


@router.get("/")
def get_subjects(faculty: str, year: str, request: Request):
    try:
        df = pd.read_csv("df.csv", delimiter=";")
        
        df = df[["katedra", "zkratka", "nazev", "vyukaZS", "vyukaLS", "kreditu", "vyucovaciJazyky", "urovenNastavena"]]
        df.columns = ["Department", "Code", "Name", "Winter term", "Summer term", "Credits", "Languages", "Level"]

        return templates.TemplateResponse(
            "pages/faculty.html",
            {"request": request, "faculty": faculty, "year": year, "df": df},
        )
    except Exception as e:
        return HTMLResponse(content=f"<h1>Error on our side</h1>", status_code=500)
