from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import *
from graia.ariadne.model import Group, Member
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

import aiohttp
from PIL import Image as IMG
from pathlib import Path
from io import BytesIO

__plugin_name__ = '咋回事小老弟'
__plugin_usage__ = '@一个人说一句小老弟试试'
channel = Channel.current()

channel.name("LittleBro")
channel.description("发送'5000m [词] [词]'制作'5000兆円欲しい'图片")
channel.author("I_love_study")

@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def xiaolaodi(app: Ariadne, group: Group, message: MessageChain, member: Member):
    if '小老弟' in message.asDisplay() and message.has(At):
        xiaolaodi = IMG.open(Path(__file__).parent/'小老弟.png')
        if At(app.adapter.mirai_session.account) in message:
            text = '我哪里像小老弟了,小老弟'
            to = member.id
            user = app.adapter.mirai_session.account
        else:
            text = ''
            to = message.get(At)[0].target
            user = member.id

        user_pic = f'http://q1.qlogo.cn/g?b=qq&nk={user}&s=640'
        to_pic = f'http://q1.qlogo.cn/g?b=qq&nk={to}&s=640'
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
        out = BytesIO()
        xiaolaodi.save(out, format='PNG')
        await app.sendGroupMessage(group, MessageChain.create([
            Plain(text = text),
            Image(data_bytes=out.getvalue())]))
