"""Contain helper functions used in common tasks."""

from pathlib import Path


def getAbsCurrentPath(append: str) -> str:
    return str((Path(__file__).parent / append).absolute())
