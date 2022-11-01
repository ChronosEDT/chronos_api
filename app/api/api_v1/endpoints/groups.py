from typing import Any, List

from fastapi import APIRouter

from app import models
from app.core.chronos import fetch_groups

router = APIRouter()


@router.get("/", response_model=List[models.EDTGroup])
def read_groups() -> Any:
    groups = fetch_groups()

    if groups is None:
        return []

    return groups
