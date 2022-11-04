from typing import Any

from fastapi import APIRouter, HTTPException, Response

from app.core.timetable import get_timetable
from app.models.reason import TimeTableStatus
from app.models.timetable import CachedTimeTable

router = APIRouter()


@router.get("/{group_id}", response_model=CachedTimeTable)
def read_timetable(*, group_id: str) -> Any:
    edt_current, status = get_timetable(group_id)

    if status == TimeTableStatus.NOT_FOUND:
        raise HTTPException(status_code=404, detail="Group unknown")
    elif status == TimeTableStatus.ERROR or edt_current is None:
        raise HTTPException(
            status_code=500, detail="Unknow server error. Please contact developer."
        )

    return edt_current


@router.get("/ics/{group_id}.ics", response_class=Response)
def get_ics_timetable(*, group_id: str) -> Any:
    edt_current, status = get_timetable(group_id)

    if status == TimeTableStatus.NOT_FOUND:
        raise HTTPException(status_code=404, detail="Group unknown")
    elif status == TimeTableStatus.ERROR or edt_current is None:
        raise HTTPException(
            status_code=500, detail="Unknow server error. Please contact developer."
        )

    return Response(content=b"hello world!", media_type="application/octet-stream")
