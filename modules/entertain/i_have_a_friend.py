import random
from dataclasses import dataclass
from io import BytesIO
from typing import Annotated

import aiohttp
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Image
from graia.ariadne.message.parser.twilight import (ArgResult, ArgumentMatch,
                                                   ElementMatch, ElementResult,
                                                   FullMatch, RegexMatch,
                                                   ResultValue, Twilight)
from graia.ariadne.model import Group, Member
from graia.saya import Channel
from graiax.shortcut.saya import dispatch, listen
from PIL import Image as IMG
from PIL import ImageDraw

from utils.text import text2pic

channel = Channel.current()

channel.name("IHaveAFriend")
channel.author("I_love_study")
channel.description(
    "一个生成假聊天记录插件，\n"
    "在群中发送 "
    "`我(有一?个)?朋友(想问问|说|让我问问|想问|让我问|想知道|让我帮他问问|让我帮他问|让我帮忙问|让我帮忙问问|问) [-dark] [@target] 内容` "
    "即可 [@目标]"
)


@dataclass
class ColorAttribute:
    background: tuple[int, int, int]
    bubble: tuple[int, int, int]
    name: tuple[int, int, int]
    text: tuple[int, int, int]


white_color = ColorAttribute(background=(241, 241, 241),
                             bubble=(255, 255, 255),
                             name=(168, 168, 168),
                             text=(0, 0, 0))
dark_color = ColorAttribute(background=(0, 0, 0),
                            bubble=(38, 38, 38),
                            name=(149, 149, 149),
                            text=(255, 255, 255))


def get_circle_xy(point: tuple[int, int], r: int):
    return (point[0] - r, point[1] - r, point[0] + r, point[1] + r)

@listen(GroupMessage)
@dispatch(
    Twilight(
        RegexMatch(r"我(有一?个)?朋友"),
        RegexMatch(
            r"(想问问|说|让我问问|想问|让我问|想知道|让我帮他问问|让我帮他问|让我帮忙问|让我帮忙问问|问)"
            ),
        FullMatch(" ", optional=True),
        ArgumentMatch("--dark", action="store_true") @ "dark",
        ElementMatch(At, optional=True) @ "target",
        RegexMatch(".+", optional=True) @ "content",
    ))
async def i_have_a_friend(
    app: Ariadne,
    group: Group,
    member: Member,
    content: Annotated[MessageChain, ResultValue()],
    target: ElementResult,
    dark: ArgResult
):
    if target.matched:
        target_class = await app.get_member(group, target.result.target) # type: ignore
    else:
        target_class = random.choice(await app.get_member_list(group))

    if not content:
        await app.send_message(group, MessageChain("说了什么？"))
        return

    color = dark_color if dark.matched else white_color

    text = text2pic(str(content),
                    color.text,
                    40,
                    width=600,
                    stroke_width=10,
                    ret_type="PIL",
                    ensure_width=False)

    name = text2pic(target_class.name, color.name, 20, width=600, height=1, ret_type="PIL", ensure_width=False)

    # 根据文字建立图片
    pic = IMG.new("RGBA", (max(200 + text.width, 170 + name.width), 100 + text.height), color.background)
    pic.paste(name, box=(160, 10), mask=name)

    # 抗锯齿粘贴头像

    async with aiohttp.request("GET", f'http://q2.qlogo.cn/headimg_dl?dst_uin={target_class.id}&spec=5') as r:
        avatar = IMG.open(BytesIO(await r.read())).resize((100, 100), IMG.Resampling.LANCZOS)
    avatar_mask = IMG.new("L", (200, 200))
    ImageDraw.Draw(avatar_mask).ellipse((0, 0, 200, 200), 255)
    pic.paste(avatar, box=(20, 10), mask=avatar_mask.resize((100, 100), IMG.LANCZOS))

    # 抗锯齿圆角举证
    round_rect_size = (40+text.width, 40+text.height)
    round_rect_size_2 = tuple(map(lambda x: x*2, round_rect_size))
    round_rect = IMG.new("RGBA", round_rect_size_2)
    ImageDraw.Draw(round_rect).rounded_rectangle((0, 0, *round_rect_size_2), 25, color.bubble)
    pic.alpha_composite(round_rect.resize(round_rect_size, IMG.LANCZOS), (150, 40))

    # 小尾巴
    tail = IMG.new("RGBA", (30, 30))
    tail_draw = ImageDraw.Draw(tail)
    tail_draw.ellipse(get_circle_xy((58, -37), 70), color.bubble)
    tail_draw.ellipse(get_circle_xy((26, -37), 46), (0, 0, 0, 0))
    tail = tail.resize((20, 20), IMG.LANCZOS)
    pic.alpha_composite(tail, (130, 60))

    pic.alpha_composite(text, (170, 60))

    pic.convert("RGB").save(b := BytesIO(), format="jpeg", quality=99)
    await app.send_message(group, MessageChain(Image(data_bytes=b.getvalue())))
