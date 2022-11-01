from typing import Any

from fastapi import APIRouter

from app import models
from app.core.timetable import get_remote_timetable

router = APIRouter()


@router.get("/{group_id}", response_model=models.TimeTable)
def read_timetable(*, group_id: str) -> Any:
    edt_current, xml_timetable = get_remote_timetable(group_id)

    if edt_current is not None:
        return edt_current
    return None
