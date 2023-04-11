import json
import re
from pathlib import Path
from typing import Any

import aiohttp
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.event.lifecycle import ApplicationLaunch
from graiax.shortcut.saya import every, listen
from loguru import logger
from lxml import html

from .utils import RelativeDate

url = "https://unpkg.com/bangumi-data@0.3/dist/data.json"

data: dict[Any, Any]

data_path = Path("data") / "bangumi_data.json"
if not data_path.exists():
    data = {"version": "0"}
else:
    data = json.loads(data_path.read_text("UTF-8"))


def get_info(bangumi_id: str) -> dict | None:
    for i in data["items"]:
        for site in i["sites"]:
            if site["site"] == "bangumi" and site["id"] == bangumi_id:
                return i

async def schedule_getter(relative_date: RelativeDate):
    async with aiohttp.request("GET", "https://bangumi.tv/calendar") as r:
        page = html.document_fromstring(await r.read())

@listen(ApplicationLaunch)
@every(mode="hour")
async def update_schedule_check():
    global data
    async with aiohttp.request("GET", url + "?meta") as r:
        search_re = re.search(r"bangumi-data@([0-9.]+)/", str(r.url))
    assert search_re
    version = search_re.group(1)

    if version == data["version"]:
        return

    logger.info("发现更新，开始下载")
    async with aiohttp.request("GET", url) as r:
        data_update = await r.json()
    data_update["version"] = version

    data = data_update
    data_path.write_text(json.dumps(data, ensure_ascii=False), "UTF-8")
    logger.success("bangumi-data更新完毕")