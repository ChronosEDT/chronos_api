import pickle
import xml.etree.ElementTree as ElementTree
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, cast

from app.core.chronos import get_remote_timetable_xml
from app.core.redis import get_redis
from app.logger import get_logger
from app.models.reason import RemoteTimeTableStatus, TimeTableStatus
from app.models.timetable import CachedTimeTable, Course, TimeTable

logger = get_logger(__name__)


def convert_xml_to_timetable(timetable_xml: str) -> Optional[TimeTable]:
    root = ElementTree.fromstring(timetable_xml)

    weeks: Dict[int, datetime] = {}
    courses: List[Course] = []

    week_nodes: List[ElementTree.Element] = root.findall("span")
    course_nodes: List[ElementTree.Element] = root.findall("event")
    options_node = root.find("option")

    if len(week_nodes) == 0 or options_node is None:
        return None

    subheading_node = options_node.find("subheading")

    if subheading_node is None or subheading_node.text is None:
        return None

    group_name: str = subheading_node.text.replace("Emploi du temps Groupe - ", "")

    for week_node in week_nodes:
        week_date_node = week_node.get("date")
        week_rawix_node = week_node.get("rawix")

        if week_date_node is None or week_rawix_node is None:
            return None

        weeks[int(week_rawix_node)] = datetime.strptime(week_date_node, "%d/%m/%Y")

    for course_node in course_nodes:
        rawweeks_element = course_node.find("rawweeks")
        day_element = course_node.find("day")

        if rawweeks_element is None or rawweeks_element.text is None:
            return None
        if day_element is None or day_element.text is None:
            return None

        week_index: int = rawweeks_element.text.index("Y") + 1
        week_date: Optional[datetime] = weeks.get(week_index)
        day: int = int(day_element.text)
        times: Optional[str] = course_node.get("timesort")

        if week_date is None or times is None:
            return None

        start_date: datetime = week_date + timedelta(days=day)
        end_date: datetime = week_date + timedelta(days=day)
        notes: Optional[str] = None
        color: str = course_node.get("colour", "FFFFFF")
        course_resources: Dict[str, List[str]] = {
            "groups": [],
            "modules": [],
            "staff": [],
            "rooms": [],
        }
        course_resources_items = {
            "group": "groups",
            "module": "modules",
            "staff": "staff",
            "room": "rooms",
        }

        start_date = start_date.replace(hour=int(times[0:2]), minute=int(times[2:4]))
        end_date = end_date.replace(hour=int(times[4:6]), minute=int(times[6:8]))

        resources = course_node.find("resources")

        if resources is None:
            return None

        for resource_key, resource_var in course_resources_items.items():
            resource_element = resources.find(resource_key)

            if resource_element is not None:
                resource_items = resource_element.findall("item")

                for resource_item in resource_items:
                    if resource_item.text is not None:
                        course_resources[resource_var].append(resource_item.text)

        notes_element = course_node.find("notes")

        if notes_element is not None and notes_element.text is not None:
            notes = notes_element.text

        courses.append(
            Course(
                week_date=week_date,
                start_date=start_date,
                end_date=end_date,
                color=color,
                groups=course_resources["groups"],
                modules=course_resources["modules"],
                staff=course_resources["staff"],
                rooms=course_resources["rooms"],
                notes=notes,
            )
        )

    week_list: List[datetime] = list(weeks.values())

    week_list.sort()
    courses.sort(key=lambda x: x.start_date)

    return TimeTable(group_name=group_name, weeks=week_list, courses=courses)


def get_cached_timetable(group_id: str) -> Optional[CachedTimeTable]:
    redis = get_redis()
    edt_key = f"cache_edt_{group_id}"

    if redis is None:
        return None

    try:
        edt_data = redis.get(edt_key)

        if edt_data is None:
            return None

        return cast(CachedTimeTable, pickle.loads(edt_data))
    except Exception:
        return None


def cache_timetable(group_id: str, timetable: TimeTable) -> Optional[CachedTimeTable]:
    redis = get_redis()
    edt_key = f"cache_edt_{group_id}"

    if redis is None:
        return None

    cached_timetable = CachedTimeTable(cache_date=datetime.now(), timetable=timetable)

    try:
        edt_data = pickle.dumps(cached_timetable)

        is_cached = redis.set(edt_key, edt_data, ex=15 * 60)

        if is_cached is not None and is_cached is True:
            return cached_timetable

        return None
    except Exception:
        return None


def get_timetable(group_id: str) -> Tuple[Optional[CachedTimeTable], TimeTableStatus]:
    cached_timetable = get_cached_timetable(group_id)

    if cached_timetable is not None:
        return cached_timetable, TimeTableStatus.CACHE_HIT

    timetable_xml, status = get_remote_timetable_xml(group_id)

    if status == RemoteTimeTableStatus.NOT_FOUND:
        return None, TimeTableStatus.NOT_FOUND
    elif status == RemoteTimeTableStatus.ERROR:
        return None, TimeTableStatus.ERROR

    if timetable_xml is None:
        return None, TimeTableStatus.ERROR

    timetable = convert_xml_to_timetable(timetable_xml)

    if timetable is None:
        return None, TimeTableStatus.ERROR

    cached_timetable = cache_timetable(group_id, timetable)

    if cached_timetable is not None:
        return cached_timetable, TimeTableStatus.CACHE_MISS

    logger.warning("Timetable caching failed!")

    return (
        CachedTimeTable(cache_date=datetime.now(), timetable=timetable),
        TimeTableStatus.CACHE_MISS,
    )
