from typing import Any

from fastapi import APIRouter

from app.core.chronos import fetch_groups
from app.models.group import EDTGroup

router = APIRouter()


@router.get("/", response_model=list[EDTGroup])
async def read_groups() -> Any:
    groups = await fetch_groups()

    if groups is None:
        return []

    return groups
