import re

import httpx

from app.config import get_settings
from app.core.network import get_client
from app.logger import get_logger
from app.models.group import EDTGroup
from app.models.reason import RemoteTimeTableStatus

logger = get_logger(__name__)

GROUPS_SELECT_HTML_REGEX = re.compile(r"<option value=\"(.+)\.html\">(.+)<\/option>")


async def fetch_groups() -> list[EDTGroup] | None:
    http_client = get_client()
    settings = get_settings()

    try:
        chronos_response = await http_client.get(str(settings.CHRONOS_GROUP_URL))

        chronos_response.raise_for_status()
        chronos_response.encoding = "utf-8"
    except httpx.NetworkError:
        logger.exception("Chronos group seems to be unreachable!")
        return None
    except httpx.TimeoutException:
        logger.exception("Chronos group has timeout!")
        return None
    except httpx.TooManyRedirects:
        logger.exception("Chronos group started too many redirects!")
        return None
    except httpx.HTTPStatusError:
        logger.exception("Chronos group did not respond with a 200 status!")
        return None
    except httpx.RequestError:
        logger.exception("Chronos group request failed for unknow reasons!")
        return None

    groups: list[EDTGroup] = []

    for htmlGroupOption in re.finditer(
        GROUPS_SELECT_HTML_REGEX, chronos_response.text, re.MULTILINE
    ):
        matchedRegexGroups = htmlGroupOption.groups()

        if len(matchedRegexGroups) == 3:
            groups.append(
                EDTGroup(id=matchedRegexGroups[1], name=matchedRegexGroups[2])
            )

    return groups


async def get_remote_timetable_xml(
    group_id: str,
) -> tuple[str | None, RemoteTimeTableStatus]:
    http_client = get_client()
    settings = get_settings()

    try:
        chronos_response = await http_client.get(
            str(settings.CHRONOS_EDT_URL).format(group_id)
        )

        if chronos_response.status_code == httpx.codes.NOT_FOUND:
            return None, RemoteTimeTableStatus.NOT_FOUND

        chronos_response.raise_for_status()
        chronos_response.encoding = "utf-8"

        return chronos_response.text, RemoteTimeTableStatus.OK
    except httpx.NetworkError:
        logger.exception("Chronos EDT seems to be unreachable!")
        return None, RemoteTimeTableStatus.ERROR
    except httpx.TimeoutException:
        logger.exception("Chronos EDT has timeout!")
        return None, RemoteTimeTableStatus.ERROR
    except httpx.TooManyRedirects:
        logger.exception("Chronos EDT started too many redirects!")
        return None, RemoteTimeTableStatus.ERROR
    except httpx.HTTPStatusError:
        logger.exception("Chronos EDT did not respond with a 200 status!")
        return None, RemoteTimeTableStatus.ERROR
    except httpx.RequestError:
        logger.exception("Chronos EDT request failed for unknow reasons!")
        return None, RemoteTimeTableStatus.ERROR
