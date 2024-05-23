from enum import Enum
from fastapi import Path
from pydantic import BaseModel, field_validator


class Faculty(str, Enum):
    fsi = "fsi"
    ff = "ff"
    prf = "prf"
    fžp = "fzp"
    fzs = "fzs"
    pf = "pf"
    fse = "fse"
    fud = "fud"
