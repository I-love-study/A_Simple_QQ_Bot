import asyncio
from io import BytesIO
from pathlib import Path
from typing import Annotated

import aiohttp
import imageio.v3 as iio
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Image
from graia.ariadne.message.parser.twilight import (FullMatch, ResultValue,
                                                   Twilight, WildcardMatch)
from graia.ariadne.model import Group, Member
from graia.saya import Channel
from graiax.shortcut.saya import listen, dispatch
from PIL import Image as IMG

channel = Channel.current()

channel.name("petpet")
channel.description("发送'摸头@某人'制作摸头GIF")
channel.author("I_love_study")

# 头像每一帧时的位置

# 每一个 tuple 内分别是:
# (x1, y1, x2, y2)
# 其中 (x1, y1) 为左上角坐标，(x2, y2) 为右下角坐标
frame_spec = [
    [27, 31, 86, 90],
    [22, 36, 91, 90],
    [18, 41, 95, 90],
    [22, 41, 91, 91],
    [27, 28, 86, 91]
]

# 挤压偏移量

# 最大挤压时头像实际位置与上述描述相差的良
squish_factor = [
    (0, 0, 0, 0),
    (-7, 22, 8, 0),
    (-8, 30, 9, 6),
    (-3, 21, 5, 9),
    (0, 0, 0, 0)
]
# 最大挤压时每一帧模板向下偏移的量
squish_translation_factor = [0, 20, 34, 21, 0]

def make_petpet(file, squish=0):
    profile_pic = IMG.open(file)
    hands = IMG.open(Path(__file__).parent/'sprite.png')
    gifs = []
    for i,spec in enumerate(frame_spec):
        # 将位置添加偏移量
        for j, s in enumerate(spec):
            spec[j] = int(s + squish_factor[i][j] * squish)
        hand = hands.crop((112*i,0,112*(i+1),112))
        reprofile = profile_pic.resize(
            (int((spec[2] - spec[0]) * 1.2), int((spec[3] - spec[1]) * 1.2)),
            IMG.Resampling.LANCZOS)
        gif_frame = IMG.new('RGB', (112, 112), (255, 255, 255))
        gif_frame.paste(reprofile, (spec[0], spec[1]))
        gif_frame.paste(hand, (0, int(squish * squish_translation_factor[i])), hand)
        gifs.append(gif_frame)
    return iio.imwrite("<bytes>", gifs, extension=".gif", loop=0, during=40, subrectangles=True)

@listen(GroupMessage)
@dispatch(Twilight(FullMatch("摸头"), WildcardMatch() @ "para"))
async def petpet(app: Ariadne, group: Group, member: Member, para: Annotated[MessageChain, ResultValue()]):
    user = para.get_first(At).target if para.has(At) else member.id
    profile_url = f"https://q2.qlogo.cn/headimg_dl?dst_uin={user}&spec=640"
    async with aiohttp.request("GET", profile_url) as r:
        profile = BytesIO(await r.read())
    gif = await asyncio.to_thread(make_petpet, profile)
    await app.send_group_message(group, MessageChain([Image(data_bytes=gif)]))