"""Modul obsahující validátory."""

from enum import Enum


class Faculty(str, Enum):
    """Enum pro fakulty."""

    all = "all"
    fsi = "fsi"
    ff = "ff"
    prf = "prf"
    fžp = "fzp"
    fzs = "fzs"
    pf = "pf"
    fse = "fse"
    fud = "fud"
