import asyncio
import json
from datetime import datetime, date, time, timedelta
from io import BytesIO
from operator import itemgetter
from pathlib import Path

import aiohttp
from aniso8601 import parse_repeating_interval
from lxml import html
from PIL import Image, ImageDraw, ImageFont
from .utils import  RelativeDate, get_max_length_text, get_antialias_rounded_rectangle
from .schedule import get_info

ttf_path = 'static/font/SourceHanSans-Medium.otf'

def get_closest_time(d: date | datetime, repeating_interval: str) -> datetime | None:
    duration = timedelta(days=3, hours=12)
    if isinstance(d, date):
        d = datetime.combine(d, time(12, 0, 0)).astimezone()
    endsdate = d + timedelta(days=7)
    for i in parse_repeating_interval(repeating_interval):
        i: datetime
        if i > endsdate:
            return
        if abs(i - d) < duration:
            return i


async def schedule_getter(relative_date: RelativeDate) -> bytes:
    async with aiohttp.request("GET", "https://bangumi.tv/calendar") as r:
        page = html.document_fromstring(await r.read())
    date_get = {
        RelativeDate.yesterday: date.today() - timedelta(days=1),
        RelativeDate.today: date.today(),
        RelativeDate.tomorrow: date.today() + timedelta(days=1)
    }[relative_date]
    bangumis = page.xpath(f"//dd[@class='{date_get.strftime('%a')}']/ul/li")
    pic = Image.new("RGB",(1200, 100 + 270 * len(bangumis)),(40,41,35))
    pic_draw = ImageDraw.Draw(pic)

    ttf_big = ImageFont.truetype(ttf_path, 60)
    ttf_small = ImageFont.truetype(ttf_path, 40)

    pic_draw.text((30, 30), "注：以下数据可能与实际有出入，请自行辨认", "white", ttf_small)

    bs = []
    async with aiohttp.ClientSession() as session:
        for b in bangumis:
            url = "https:" + b.get("style").split("'")[1]
            title = b.xpath(".//a[@class='nav']//text()")
            bangumi_id = b.xpath(".//a[@class='nav']/@href")[0].split("/")[-1]
            bangumi_info = get_info(bangumi_id)
            async with session.get(url) as r:
                if r.status == 200:
                    poster = await r.read()
                else:
                    poster = None
            if bangumi_info and "broadcast" in bangumi_info:
                t = get_closest_time(date.today(), bangumi_info["broadcast"])
                if t is None:
                    t = datetime.max.replace(tzinfo=datetime.now().astimezone().tzinfo)
            else:
                t = datetime.max.replace(tzinfo=datetime.now().astimezone().tzinfo)
            bs.append({"titles": title, "id": bangumi_id, "image": poster, "time": t})

    bs.sort(key=itemgetter("time"))

    for n, bangumi in enumerate(bs):
        title = bangumi["titles"]
        if bangumi["image"] is not None:
            poster = Image.open(BytesIO(bangumi["image"]))
        else:
            poster = Image.new("RGB", (150, 210))

        # 比例一般为 5:7
        if poster.size != (150, 210):
            poster = poster.resize((150, 210), Image.Resampling.LANCZOS)
        mask = get_antialias_rounded_rectangle((150, 210))
        pic.paste(poster, (30, 130 + 270 * n), mask=mask)

        pic_draw.text(
            (210, 130+270*n),
            get_max_length_text(title[0], 950, ttf_big),
            font=ttf_big,
            fill=(255,255,255))

        if len(title) > 1 and title[0] != title[1]:
            pic_draw.text(
                (210, 200+270*n),
                get_max_length_text(title[1], 950, ttf_small),
                font=ttf_small,
                fill=(200,200,200))

        if bangumi["time"].year != 9999:
            pic_draw.text((210, 250 + 270 * n),
                bangumi["time"].strftime("%a %H:%M"),
                font=ttf_small,
                fill=(0, 160, 216))

    pic.save(out := BytesIO(), format='JPEG')
    return out.getvalue()