from typing import List, Optional, Tuple, cast

import requests
from bs4 import BeautifulSoup, Tag

from app.core.config import get_settings
from app.core.network import get_client
from app.logger import get_logger
from app.models.group import EDTGroup
from app.models.reason import RemoteTimeTableStatus

logger = get_logger(__name__)


def fetch_groups() -> Optional[List[EDTGroup]]:
    http_client = get_client()
    settings = get_settings()

    try:
        chronos_response = http_client.get(settings.CHRONOS_GROUP_URL)

        chronos_response.raise_for_status()
        chronos_response.encoding = "utf-8"
    except requests.exceptions.ConnectionError:
        logger.exception("Chronos group seems to be unreachable!")
        return None
    except requests.exceptions.Timeout:
        logger.exception("Chronos group has timeout!")
        return None
    except requests.exceptions.TooManyRedirects:
        logger.exception("Chronos group started too many redirects!")
        return None
    except requests.exceptions.HTTPError:
        logger.exception("Chronos group did not respond with a 200 status!")
        return None
    except requests.exceptions.RequestException:
        logger.exception("Chronos group request failed for unknow reasons!")
        return None

    try:
        chronos_html = chronos_response.text
        soup = BeautifulSoup(chronos_html, features="html.parser")
    except Exception:
        logger.exception("Unexcepted error while parsing chronos group html response!")
        return None

    html_select = cast(Tag, soup.find("select", attrs={"name": "menu2"}))

    if html_select is None:
        logger.warning("Chronos group: Failed to find the select tag")
        return None

    html_select_options = html_select.findAll("option")

    if len(html_select_options) == 0:
        logger.warning("Chronos group: Failed to find any options")
        return None

    html_options = html_select_options[1:]

    return [EDTGroup(id=g["value"].split(".")[0], name=g.text) for g in html_options]


def get_remote_timetable_xml(
    group_id: str,
) -> Tuple[Optional[str], RemoteTimeTableStatus]:
    http_client = get_client()
    settings = get_settings()

    try:
        chronos_response = http_client.get(settings.CHRONOS_EDT_URL.format(group_id))

        if chronos_response.status_code == requests.status_codes.codes.not_found:
            return None, RemoteTimeTableStatus.NOT_FOUND

        chronos_response.raise_for_status()
        chronos_response.encoding = "utf-8"

        return chronos_response.text, RemoteTimeTableStatus.OK
    except requests.exceptions.ConnectionError:
        logger.exception("Chronos EDT seems to be unreachable!")
        return None, RemoteTimeTableStatus.ERROR
    except requests.exceptions.Timeout:
        logger.exception("Chronos EDT has timeout!")
        return None, RemoteTimeTableStatus.ERROR
    except requests.exceptions.TooManyRedirects:
        logger.exception("Chronos EDT started too many redirects!")
        return None, RemoteTimeTableStatus.ERROR
    except requests.exceptions.HTTPError:
        logger.exception("Chronos EDT did not respond with a 200 status!")
        return None, RemoteTimeTableStatus.ERROR
    except requests.exceptions.RequestException:
        logger.exception("Chronos EDT request failed for unknow reasons!")
        return None, RemoteTimeTableStatus.ERROR
