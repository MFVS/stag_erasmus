"""Modul obsahující validátory."""

from enum import Enum


class Faculty(str, Enum):
    """Enum pro fakulty."""

    all = "all"
    fud = "fud"
    ff = "ff"
    fse = "fse"
    fzp = "fzp"
    fzs = "fzs"
    pf = "pf"
    prf = "prf"
    fsi = "fsi"
