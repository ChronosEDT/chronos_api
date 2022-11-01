from fastapi import APIRouter

from app.api.api_v1.endpoints import groups, timetable

api_router = APIRouter()
api_router.include_router(groups.router, prefix="/groups", tags=["groups"])
api_router.include_router(timetable.router, prefix="/timetables", tags=["timetables"])
