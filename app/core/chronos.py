from typing import List, Optional, cast

import requests
from bs4 import BeautifulSoup, Tag

from app import models
from app.core.network import get_client


def fetch_groups() -> Optional[List[models.EDTGroup]]:
    http_client = get_client()

    try:
        chronos_response = http_client.get(
            "http://chronos.iut-velizy.uvsq.fr/EDT/gindex.html"
        )

        chronos_response.raise_for_status()
        chronos_response.encoding = "utf-8"
    except requests.exceptions.RequestException:
        return None

    try:
        chronos_html = chronos_response.text
        soup = BeautifulSoup(chronos_html, features="html.parser")
    except Exception:
        return None

    html_select = cast(Tag, soup.find("select", attrs={"name": "menu2"}))

    if html_select is None:
        return None

    html_select_options = html_select.findAll("option")

    if len(html_select_options) == 0:
        return None

    html_options = html_select_options[1:]

    return [
        models.EDTGroup(id=g["value"].split(".")[0], name=g.text) for g in html_options
    ]
