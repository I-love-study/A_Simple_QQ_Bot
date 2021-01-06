from graia.application import GraiaMiraiApplication
from graia.application.event.messages import GroupMessage
from graia.application.message.elements.internal import Plain, At, Image
from graia.application.message.chain import MessageChain
from graia.application.group import Group, Member
from core import judge
from core import get

import aiohttp
from PIL import Image as IMG
from pathlib import Path
from io import BytesIO

__plugin_name__ = '咋回事小老弟'
__plugin_usage__ = '@一个人说一句小老弟试试'

bcc = get.bcc()
@bcc.receiver(GroupMessage, headless_decoraters = [judge.group_check(__name__)])
async def xiaolaodi(app: GraiaMiraiApplication, group: Group, message: MessageChain, member: Member):
    if '小老弟' in message.asDisplay() and message.has(At):
        xiaolaodi = IMG.open(Path(__file__).parent/'小老弟.png')
        if (at_u := message.get(At)[0].target) == app.connect_info.account:
            text = '我哪里像小老弟了,小老弟'
            to = member.id
            user = at_u
        else:
            text = ''
            to = at_u
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
            Image.fromUnsafeBytes(out.getvalue())]))
