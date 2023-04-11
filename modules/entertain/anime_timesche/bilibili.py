import asyncio
import time
from datetime import date
from io import BytesIO

import aiohttp
from graia.ariadne.message.element import Image
from PIL import Image, ImageDraw, ImageFont

from .utils import (RelativeDate, get_antialias_rounded_rectangle,
                    get_max_length_text, pic_url2bytes)


async def schedule_getter(relative_date: RelativeDate) -> bytes:
    today = int(time.mktime(date.today().timetuple()))
    date2ts = {
        RelativeDate.yesterday: today - 86400,
        RelativeDate.today: today,
        RelativeDate.tomorrow: today + 86400,
    }
    date_ts = date2ts[relative_date]

    ttf = ImageFont.truetype('static/font/SourceHanSans-Medium.otf', 60)
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=0)) as session:
        async with session.get('https://bangumi.bilibili.com/web_api/timeline_global') as r:
            result = (await r.json())['result']
        data = next(anime_ts['seasons'] for anime_ts in result if anime_ts['date_ts'] == date_ts)
        await asyncio.gather(*[pic_url2bytes(n, "square_cover", session) for n in data])

    final_back = Image.new("RGB", (1200, 300 * len(data)), (40, 41, 35))
    final_draw = ImageDraw.Draw(final_back)
    for n, single in enumerate(data):
        pic = Image.open(BytesIO(single["pic_bytes"]))
        if pic.size != (240, 240):
            pic = pic.resize((240, 240), Image.Resampling.LANCZOS)
        mask = get_antialias_rounded_rectangle((240, 240))
        final_back.paste(pic, (30, 30 + 300 * n), mask=mask)

        title_s = get_max_length_text(single['title'], 900, ttf)
        final_draw.text((300, 50 + 300 * n), title_s, font=ttf, fill="white")
        final_draw.text((300, 150 + 300 * n), single['pub_time'], font=ttf, fill="white")
        final_draw.text((300 + ttf.getsize(single['pub_time'])[0] + 30, 150 + 300 * n),
                        single['pub_index'] if 'pub_index' in single else single['delay_index'] +
                        single['delay_reason'],
                        font=ttf,
                        fill=(0, 160, 216))
    final_back.save(out := BytesIO(), format='JPEG')
    return out.getvalue()
