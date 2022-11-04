from enum import Enum, auto


class RemoteTimeTableStatus(Enum):
    OK = auto()
    NOT_FOUND = auto()
    ERROR = auto()


class TimeTableStatus(Enum):
    CACHE_HIT = auto()
    NOT_FOUND = auto()
    CACHE_MISS = auto()
    ERROR = auto()
