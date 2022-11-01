from datetime import datetime
from typing import List, Optional

import ujson
from pydantic import BaseModel


class Course(BaseModel):
    week_date: datetime
    start_date: datetime
    end_date: datetime
    group: Optional[str]
    module: Optional[str]
    staff: Optional[str]
    room: Optional[str]

    class Config:
        allow_mutation = False
        json_loads = ujson.loads


class TimeTable(BaseModel):
    group_name: str
    weeks: List[datetime]
    courses: List[Course]

    class Config:
        allow_mutation = False
        json_loads = ujson.loads
