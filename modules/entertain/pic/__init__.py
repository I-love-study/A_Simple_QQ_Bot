from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Image
from graia.ariadne.model import Group, Member
from graia.saya import Channel
from graiax.shortcut.saya import listen

import aiohttp
from PIL import Image as IMG
from pathlib import Path
from io import BytesIO

channel = Channel.current()

channel.name("LittleBro")
channel.description("@一个人说一句小老弟试试")
channel.author("I_love_study")

@listen(GroupMessage)
async def xiaolaodi(app: Ariadne, group: Group, message: MessageChain, member: Member):
    if '小老弟' in message.display and message.has(At):
        xiaolaodi = IMG.open(Path(__file__).parent/'小老弟.png')
        if At(app.account) in message:
            text = '我哪里像小老弟了,小老弟'
            to = member.id
            user = app.account
        else:
            text = ''
            to = message.get(At)[0].target
            user = member.id

        user_pic = f"https://q2.qlogo.cn/headimg_dl?dst_uin={user}&spec=640"
        to_pic = f"https://q2.qlogo.cn/headimg_dl?dst_uin={to}&spec=640"
        async with aiohttp.request("GET",user_pic) as r:
            user_pic = await r.read()
            user_pic = IMG.open(BytesIO(user_pic))
        async with aiohttp.request("GET",to_pic) as r:
            to_pic = await r.read()
            to_pic = IMG.open(BytesIO(to_pic))
        user_box = (18,9,87,78)
        to_box = (173,23,232,82)
        user_pic = user_pic.resize((user_box[2] - user_box[0],
                                    user_box[3] - user_box[1]))
        to_pic = to_pic.resize((to_box[2] - to_box[0],
                                to_box[3] - to_box[1]))
        xiaolaodi.paste(user_pic,user_box)
        xiaolaodi.paste(to_pic,to_box)
        xiaolaodi.save(out := BytesIO(), format='PNG')
        await app.send_group_message(group, MessageChain(text, Image(data_bytes=out.getvalue())))
