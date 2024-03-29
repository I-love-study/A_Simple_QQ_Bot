import asyncio
from io import BytesIO
from pathlib import Path

import aiohttp
import imageio.v3 as iio
import numpy as np
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, At
from graia.ariadne.message.parser.base import ContainKeyword
from graia.ariadne.model import Group, Member
from graia.saya import Channel
from graiax.shortcut.saya import listen, decorate
from PIL import Image as IMG
from PIL import ImageSequence

channel = Channel.current()
channel.name("Worship")
channel.description("发送膜拜+任意at一个，返回唐可可膜拜你")
channel.author("I_love_study")

@listen(GroupMessage)
@decorate(ContainKeyword("膜拜"))
async def ll_worship(app: Ariadne, group: Group, member: Member, message: MessageChain):
    if message[At]:
        url = f"https://q2.qlogo.cn/headimg_dl?dst_uin=={message[At][0].target}&spec=640"
        async with aiohttp.request("GET", url) as r:
            avatar = await r.read()
    else:
        avatar = await member.get_avatar()
    
    await app.send_group_message(group, MessageChain(
        f"{member.name} 膜拜了你！" if message[At] else "你膜拜了自己！",
        Image(data_bytes=await asyncio.to_thread(create_meme, avatar))
    ))

def find_coeffs(source_coords, target_coords):
    matrix = []
    for s, t in zip(source_coords, target_coords):
        matrix += ([t[0], t[1], 1, 0, 0, 0, -s[0] * t[0], -s[0] * t[1]], 
                   [0, 0, 0, t[0], t[1], 1, -s[1] * t[0], -s[1] * t[1]])
    A = np.matrix(matrix, dtype=np.float64)
    B = np.array(source_coords).reshape(8)
    res = np.dot(np.linalg.inv(A.T * A) * A.T, B)
    return np.array(res).reshape(8)

def create_meme(avatar_bytes: bytes):
    avatar = IMG.open(BytesIO(avatar_bytes))
    background = IMG.open(Path(__file__).parent / "worship.webp")

    w, h = avatar.size
    coeffs = find_coeffs(
        [(0, 0), (w, 0), (w, h), (0, h)],
        [(50, -33), (275, 36), (275, 298), (50, 283)]
        #[(150, -100), (826, 121), (826, 894), (150, 850)]
    )
    bg = avatar.transform((640, 320), IMG.Transform.PERSPECTIVE, coeffs, IMG.Resampling.BICUBIC)
    frames = []
    for frame in ImageSequence.Iterator(background):
        n_frame = bg.copy()
        n_frame.paste(frame, (0, 0), frame)
        frames.append(n_frame)
    return iio.imwrite("<bytes>", frames, extension=".gif", loop=0, duration=50, subrectangles=True)