from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import *
from graia.ariadne.message.parser.pattern import FullMatch, WildcardMatch
from graia.ariadne.message.parser.twilight import Sparkle, Twilight
from graia.ariadne.model import Group, Member
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

from urllib.parse import quote

from playwright.async_api import async_playwright

channel = Channel.current()
channel.name("MoegirlInfo")
channel.description("获取萌娘百科上人物介绍卡片")
channel.author("I_love_study")

@channel.use(ListenerSchema(
    listening_events=[GroupMessage],
    inline_dispatchers=[Twilight(Sparkle(
        [FullMatch("萌娘百科")], {"para": WildcardMatch()}
    ))]
))
async def moegirl_search(app: Ariadne, group: Group, para: WildcardMatch):
    url = "https://zh.moegirl.org.cn/zh-cn/"+ quote(para.result.asDisplay().strip())
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(device_scale_factor=2.0)
        page = await context.new_page()
        await app.sendGroupMessage(group, MessageChain.create([
            Plain("正在加载中，请稍后")
        ]))

        try:
            #因为萌娘有点慢所以给20s加载并且使用domcontentloaded(可能会出现加载不出来图片)
            await page.goto(url, wait_until='domcontentloaded', timeout=20000)
        except Exception:
            await app.sendGroupMessage(group, MessageChain.create([
                Plain("错误：无法打开页面(可能是页面加载时间太久)，请稍后再试")
            ]))
            await browser.close()
            return
        
        await page.set_viewport_size({"width": 2560, "height": 1920})
        selector = ["table.infobox2", "table.infobox", "div.infotemplatebox"]
        for s in selector:
            card = await page.query_selector(s)
            if card is not None:
                break
        else:
            await app.sendGroupMessage(group, MessageChain.create([
                Plain("错误：找不到人物信息卡片")
            ]))
            await browser.close()
            return
        clip = await card.bounding_box()
        assert clip is not None
        pic = await page.screenshot(clip=clip, type='png', full_page=True)
        await browser.close()
    
    await app.sendGroupMessage(group, MessageChain.create([
        Image(data_bytes=pic)
    ]))