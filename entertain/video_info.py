from graia.broadcast.builtin.decoraters import Depend
from graia.application import GraiaMiraiApplication
from graia.application.event.messages import GroupMessage
from graia.application.message.elements.internal import Plain, At, Image
from graia.application.message.chain import MessageChain
from graia.application.message.parser.kanata import Kanata
from graia.application.message.parser.signature import RegexMatch
from graia.application.group import Group, Member
from graia.template import Template
from expand import judge
from expand import tencent_ai
from core import get

import re
import aiohttp

__plugin_name__ = 'B站视频信息查看'
__plugin_usage__ = '发送任意av/BV号获取视频信息'

bcc = get.bcc()
@bcc.receiver(GroupMessage, headless_decoraters = [Depend(judge.active_check_message)])
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
    print(get)
    title = get['data']['title']
    aid = get['data']['aid']
    bvid = get['data']['bvid']
    up = get['data']['owner']['name']
    during = '{}分{}秒'.format(get['data']['duration'] // 60 ,get['data']['duration'] % 60)
    async with aiohttp.request("GET",get['data']['pic']) as r:
        p_data = await r.read()
    porn = await tencent_ai.ero_pic(p_data,'data')
    normal,hot,porn = porn['data']['tag_list'][:3]
    if ((normal['tag_confidence'] <= 10
      or porn['tag_confidence'] >= 70)
      and normal['tag_confidence'] <= 10):
        target = Plain('[涩情封面]\n')
    else:
        target = Image.fromUnsafeBytes(p_data)
    await app.sendGroupMessage(group, Template(f'$target标题:{title}\nUp主:{up}\n视频时长:{during}\nav号:{aid}\nbv号:{bvid}\n链接:https://bilibili.com/video/{bvid}').render(target = target))