import asyncio
from typing import Annotated

from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image
from graia.ariadne.message.parser.twilight import (ArgResult, ArgumentMatch,
                                                   ElementMatch, ElementResult,
                                                   FullMatch, RegexMatch,
                                                   ResultValue, Twilight)
from graia.ariadne.model import Group
from graia.saya import Channel
from graiax.shortcut.saya import dispatch, listen

from .gen import gen_verification


#from pathlib import Path
#Path("test.jpg").write_bytes(gen_verification("涩图", Path(r"E:\Files\Desktop\FrbK_XKagAAbmAi.jpg").read_bytes(), "zh"))
#exit()

channel = Channel.current()

channel.name("GoogleVerification")
channel.author("SAGIRI-kawaii, I_love_study")


@listen(GroupMessage)
@dispatch(
    Twilight(FullMatch("谷歌验证码"),
             ArgumentMatch("-e", "--en", "--english", action="store_true", optional=True) @ "en",
             RegexMatch(".+") @ "title", FullMatch("\n", optional=True),
             ElementMatch(Image) @ "image"))
async def google_verification(app: Ariadne, group: Group, en: ArgResult,
                              title: Annotated[MessageChain, ResultValue()], image: ElementResult):
    assert isinstance(image.result, Image)
    await app.send_group_message(
        group,
        MessageChain(
            Image(data_bytes=await asyncio.to_thread(
                gen_verification,
                str(title).strip(), await image.result.get_bytes(), "en" if en.matched else "zh"))))

