import xml.etree.ElementTree as ElementTree
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import requests

from app import models
from app.core.network import get_client


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
        group: Optional[str] = None
        module: Optional[str] = None
        staff: Optional[str] = None
        room: Optional[str] = None

        start_date = start_date.replace(hour=int(times[0:2]), minute=int(times[2:4]))
        end_date = end_date.replace(hour=int(times[4:6]), minute=int(times[6:8]))

        resources = course_node.find("resources")

        if resources is None:
            return None

        group_element = resources.find("group")
        module_element = resources.find("module")
        staff_element = resources.find("staff")
        room_element = resources.find("room")

        if group_element is not None:
            group_item = group_element.find("item")

            if group_item is not None and group_item.text is not None:
                group = group_item.text

        if module_element is not None:
            module_item = module_element.find("item")

            if module_item is not None and module_item.text is not None:
                module = module_item.text

        if staff_element is not None:
            staff_item = staff_element.find("item")

            if staff_item is not None and staff_item.text is not None:
                staff = staff_item.text

        if room_element is not None:
            room_item = room_element.find("item")

            if room_item is not None and room_item.text is not None:
                room = room_item.text

        courses.append(
            models.Course(
                week_date=week_date,
                start_date=start_date,
                end_date=end_date,
                group=group,
                module=module,
                staff=staff,
                room=room,
            )
        )

    week_list: List[datetime] = list(weeks.values())

    week_list.sort()
    courses.sort(key=lambda x: x.start_date)

    return models.TimeTable(group_name=group_name, weeks=week_list, courses=courses)


def get_remote_timetable(
    group_id: str,
) -> Tuple[Optional[models.TimeTable], Optional[str]]:
    http_client = get_client()
    try:
        response = http_client.get(
            f"http://chronos.iut-velizy.uvsq.fr/EDT/{group_id}.xml"
        )

        if response.status_code != 200:
            return None, None

        response.encoding = "utf-8"

        return convert_xml_to_timetable(response.text), response.text
    except requests.exceptions.ConnectionError:
        return None, None
    except requests.exceptions.Timeout:
        return None, None
    except requests.exceptions.TooManyRedirects:
        return None, None
