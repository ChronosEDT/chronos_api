from typing import Any, List

from fastapi import APIRouter

from app.core.chronos import fetch_groups
from app.models.group import EDTGroup

router = APIRouter()


@router.get("/", response_model=List[EDTGroup])
def read_groups() -> Any:
    groups = fetch_groups()

    if groups is None:
        return []

    return groups
