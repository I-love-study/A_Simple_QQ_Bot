from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image
from graia.ariadne.message.parser.base import MatchContent
from graia.ariadne.model import Group
from graia.saya import Channel, channel
from graiax.shortcut.saya import listen, decorate

from urllib.parse import quote
from datetime import date
from io import BytesIO

import aiohttp
from lxml import etree
from PIL import Image as IMG, ImageFont, ImageDraw

channel = Channel.current()

channel.name("Birthday_searcher")
channel.description("coming soon")
channel.author("I_love_study")

@listen(GroupMessage)
@decorate(MatchContent("今天谁生日"))
async def today_birthday(app: Ariadne, group: Group):
    t = date.today()
    headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/81.0.4044.69 Safari/537.36 Edg/81.0.416.34'}
    url = f'https://zh.moegirl.org.cn/zh-cn/Category:{quote(f"{t.month}月{t.day}日")}'

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
        try:
            async with session.get(url, headers=headers) as r:
                html = etree.HTML(await r.text()) # type: ignore
        except aiohttp.ClientConnectorError:
            await app.send_group_message(group, MessageChain("对不起，现在萌娘炸了，所以您的请求我无法回复"))
            return

    figures = html.xpath('//div[@id="mw-pages"]//a/text()')
    font = ImageFont.truetype(r"static/font/SourceHanSans-Medium.otf", size=50)
    text = "\n".join(figures)
    img = IMG.new("RGB", tuple(map(lambda x: x+20, font.getsize_multiline(text))), "#FFFFFF")
    ImageDraw.Draw(img).text((10,10), text, fill = "#000000", font=font)
    img.save(b := BytesIO(), format="jpeg")
    await app.send_group_message(group, MessageChain([
        "以下为今天生日的虚拟人物哦",
        Image(data_bytes=b.getvalue())
    ]))