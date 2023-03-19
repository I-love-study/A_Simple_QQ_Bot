import asyncio
import contextlib

from arclet.alconna import (Arg, Args, Arparma, CommandMeta, Field, MultiVar,
                            Option)
from arclet.alconna.graia import Alconna, alcommand
from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image
from graia.ariadne.model import Group
from graia.saya import Channel
from nepattern import RegexPattern

from .utils import make_pic

channel = Channel.current()

channel.name("5000M")
channel.description("发送'5000m [词] [词]'制作'5000兆円欲しい'图片")
channel.author("I_love_study")

counting = RegexPattern(r"(?P<num>\d+)(?P<unit>.+)", alias="倒计时")
cd = Alconna(
    [""],
    "倒计时",
    Arg("content#中文内容", str),
    Arg("state", str, "还有"),
    Arg("count", counting, Field({"num": "5", "unit": "秒"}, alias="5秒"), notice="倒计时"),
    Option("-gif", help_text="是否为gif形式"),
    Option("英文", Args["en",  MultiVar(str)] / "\n", help_text="英文内容"),
    meta=CommandMeta("流浪地球倒计时", usage="注意: 该命令不需要 “渊白” 开头", example="倒计时 离开学 还剩 1天"),
)

@alcommand(cd, private=False)
async def countdown(app: Ariadne, group: Group, arp: Arparma):
    content = arp.content
    start = arp.state
    count = arp.count
    with contextlib.suppress(Exception):
        count = counting.match(start)
        start = "还有"
    en = "\n".join(arp.query("英文.en", []))
    gif = arp.components.get("gif")
    img = await asyncio.to_thread(make_pic, content, start, count["num"], count["unit"], en, False, gif) # type: ignore
    return await app.send_message(group, MessageChain(Image(data_bytes=img)))