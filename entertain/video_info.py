from graia.application import GraiaMiraiApplication
from graia.application.event.messages import GroupMessage
from graia.application.message.elements.internal import Plain, Image
from graia.application.message.chain import MessageChain
from graia.application.group import Group, Member
from core import judge
from core import get

import re
import aiohttp

__plugin_name__ = 'B站视频信息查看'
__plugin_usage__ = '发送任意av/BV号获取视频信息'

bcc = get.bcc()
@bcc.receiver(GroupMessage, headless_decoraters = [judge.group_check(__name__)])
async def video_info(app: GraiaMiraiApplication, group: Group, message: MessageChain, member:Member):
    if message.asDisplay().startswith(('av','AV','Av')):
        try:
            id_type = 'aid'
            num = int(re.sub('av', '', message.asDisplay(), flags = re.I))
        except ValueError:
            return
    elif message.asDisplay().startswith('BV') and len(msg) == 12:
        id_type = 'bvid'
        num = message.asDisplay()
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