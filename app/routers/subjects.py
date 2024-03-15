from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
import pandas as pd

router = APIRouter(prefix="/subjects", tags=["Subjects"])

templates = Jinja2Templates(directory="app/templates")


@router.get("/")
def get_subjects(faculty: str, year: str, request: Request):
    df = pd.read_csv("df.csv")
    
    df = df[["katedra", "zkratka", "nazev", "vyukaZS", "vyukaLS"]]
    df.columns = ["Department", "Code", "Name", "Winter term", "Summer term"]

    return templates.TemplateResponse(
        "pages/faculty.html",
        {"request": request, "faculty": faculty, "year": year, "df": df},
    )
