from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class Course(BaseModel):
    week_date: datetime
    start_date: datetime
    end_date: datetime
    color: str
    groups: List[str]
    modules: List[str]
    staff: List[str]
    rooms: List[str]
    notes: Optional[str]

    model_config = ConfigDict(frozen=True)


class TimeTable(BaseModel):
    group_name: str
    weeks: List[datetime]
    courses: List[Course]

    model_config = ConfigDict(frozen=True)


class CachedTimeTable(BaseModel):
    cache_date: datetime
    timetable: TimeTable

    model_config = ConfigDict(frozen=True)
