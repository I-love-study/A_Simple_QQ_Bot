from typing import Annotated
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.parser.base import DetectSuffix
from graia.ariadne.model import Group
from graia.saya import Channel
from graiax.shortcut.saya import listen

from lxml import etree
from yarl import URL
import aiohttp

channel = Channel.current()
channel.name("HotwordSearch")
channel.description("获取热词解释")
channel.author("I_love_study")

@listen(GroupMessage)
async def hotword(app: Ariadne, group: Group, message: Annotated[MessageChain, DetectSuffix("是什么梗")]):
    await app.send_message(group, MessageChain("我不造啊"))
    return

    url = URL("https://jikipedia.com/search") % {"phrase": str(message)}
    headers = {
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.53"
    }
    async with aiohttp.request("GET", url, headers=headers) as r:
        html = etree.HTML(await r.text()) # type: ignore
    
    for i in range(1, 11):
        title = html.xpath(f'//div[@class="masonry"]/div[{i}]//strong[@class="title pre"]//text()')
        desc = html.xpath(f'//div[@class="masonry"]/div[{i}]//span[contains(@class,"text brax-node pre")]//text()')
        if title and desc:
            return await app.send_group_message(group, MessageChain(f"{''.join(title)}\n\n{''.join(desc)}"))

    await app.send_group_message(group, MessageChain("错误：找不到相关结果"))

    