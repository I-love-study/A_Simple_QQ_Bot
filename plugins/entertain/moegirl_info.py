from typing import Annotated
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image
from graia.ariadne.message.parser.twilight import Twilight, ResultValue
from graia.ariadne.model import Group
from graia.saya import Channel
from graiax.shortcut.saya import listen, dispatch

from urllib.parse import quote
import aiohttp
from lxml import html
from playwright.async_api import async_playwright

channel = Channel.current()
channel.name("MoegirlInfo")
channel.description("获取萌娘百科上人物介绍卡片")
channel.author("I_love_study")

header = {
    "user-agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/103.0.5060.66 Safari/537.36 Edg/103.0.1264.44"
}


@listen(GroupMessage)
@dispatch(Twilight.from_command("萌娘百科 {para}"))
async def moegirl_search(app: Ariadne, group: Group, para: Annotated[MessageChain, ResultValue()]):
    url = f"https://zh.moegirl.org.cn/zh-cn/{quote(str(para).strip())}"
    async with aiohttp.request("GET", url, headers=header) as r:
        page = html.document_fromstring(await r.text())

    selector = '//*[@class="infotemplatebox" or @class="infoboxSpecial" or @class="infobox2" or @class="infobox"]'
    if (xp := page.xpath(selector)) != []:
        for child in page.body.getchildren():
            page.body.remove(child)
        page.body.extend(xp)
    page.make_links_absolute("https://zh.moegirl.org.cn/")
    for e in page.xpath("//div[@class='TabContentText']"):
        e.set("style", "display:block")
    content = html.tostring(page, method="HTML", encoding="unicode")
    assert not isinstance(content, bytes)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(device_scale_factor=2.0)
        page = await context.new_page()
        await page.set_content(content)
        card = await page.query_selector("xpath=/html/body/node()[1]")
        assert card
        pic = await card.screenshot(type='png')
        await browser.close()

    await app.send_group_message(group, MessageChain(Image(data_bytes=pic)))