from typing import Any

from fastapi import APIRouter, HTTPException

from app import models
from app.core.timetable import get_timetable

router = APIRouter()


@router.get("/{group_id}", response_model=models.CachedTimeTable)
def read_timetable(*, group_id: str) -> Any:
    edt_current = get_timetable(group_id)

    if edt_current is not None:
        return edt_current

    raise HTTPException(status_code=404, detail="Group unknown")
