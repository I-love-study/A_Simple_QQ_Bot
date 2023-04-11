from PIL import Image, ImageDraw, ImageFont
import aiohttp
from enum import Enum

class RelativeDate(Enum):
    yesterday = 1
    today = 2
    tomorrow = 3

def get_max_length_text(text: str, max_length: int, font: ImageFont.FreeTypeFont):
    if font.getlength(text) >= max_length:
        ellipsis_size = font.getlength('...')
        while font.getlength(text) > max_length - ellipsis_size:
            text = text[:-1]
        text = text + '...'
    return text


def get_antialias_rounded_rectangle(xy: tuple[int, int], radius: int | float = 25) -> Image.Image:
    xyx2 = (xy[0] * 2, xy[1] * 2)
    mask = Image.new("L", xyx2)
    ImageDraw.Draw(mask).rounded_rectangle(((0, 0), xyx2), radius * 2, 255)
    return mask.resize(xy, Image.Resampling.LANCZOS)


async def pic_url2bytes(d: dict, key: str, session: aiohttp.ClientSession) -> None:
    async with session.get(d[key]) as r:
        d["pic_bytes"] = await r.read()
