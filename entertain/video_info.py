from graia.application import GraiaMiraiApplication
from graia.application.event.messages import GroupMessage
from graia.application.message.elements.internal import Plain, Image
from graia.application.message.chain import MessageChain
from graia.application.group import Group, Member
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

import re
import aiohttp

channel = Channel.current()

channel.name("AVBV")
channel.description("发送任意av/BV号获取视频信息")
channel.author("I_love_study")

@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def video_info(app: GraiaMiraiApplication, group: Group, message: MessageChain, member:Member):
    msg_str = message.asDisplay().strip()
    if msg_str.startswith(('av','AV','Av')):
        try:
            id_type = 'aid'
            num = int(re.sub('av', '', msg_str, flags = re.I))
        except ValueError:
            return
    elif msg_str.startswith('BV') and len(msg_str) == 12:
        id_type = 'bvid'
        num = msg_str
    else:
        return

    url = f'https://api.bilibili.com/x/web-interface/view?{id_type}={num}'
    async with aiohttp.request("GET",url) as r:
        get = await r.json()
    data = get['data']
    during = '{}分{}秒'.format(data['duration'] // 60 ,data['duration'] % 60)

    await app.sendGroupMessage(group, MessageChain.create([
        Image.fromNetworkAddress(get['data']['pic']),
        Plain(f"\n标题:{data['title']}"),
        Plain(f"\nUp主:{data['owner']['name']}"),
        Plain(f"\n视频时长:{during}"),
        Plain(f"\nav号:{data['aid']}"),
        Plain(f"\nbv号:{data['bvid']}"),
        Plain(f"\n链接:https://bilibili.com/video/{data['bvid']}")
        ]))