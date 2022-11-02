import xml.etree.ElementTree as ElementTree
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from app import models


def convert_xml_to_timetable(timetable_xml: str) -> Optional[models.TimeTable]:
    root = ElementTree.fromstring(timetable_xml)

    weeks: Dict[int, datetime] = {}
    courses: List[models.Course] = []

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
            models.Course(
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

    return models.TimeTable(group_name=group_name, weeks=week_list, courses=courses)


def get_cached_timetable(group_id: str) -> Optional[models.CachedTimeTable]:
    return None


def get_timetable(group_id: str) -> Optional[models.CachedTimeTable]:
    return None
