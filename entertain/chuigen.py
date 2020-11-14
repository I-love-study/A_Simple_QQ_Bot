from graia.application import GraiaMiraiApplication
from graia.application.event.messages import GroupMessage
from graia.application.message.elements.internal import Plain, At
from graia.application.message.chain import MessageChain
from graia.application.group import Group, Member
from core import judge
from core import get

import time
import datetime
import aiohttp
import ujson as json

__plugin_name__ = '根瘤菌催更查看器'
__plugin_usage__ = '查看根瘤菌到底多久没更新'

headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) ' \
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}

uid=23315579#根瘤菌

dy_type={'1':'转发',
         '2':'图片动态',
         '4':'普通动态',
         '8':'视频（包括短视频）',
         '64':'文章',
         '256':'音频',
         '2048':'评分什么的'}

bcc = get.bcc()
@bcc.receiver(GroupMessage, headless_decoraters = [judge.group_check(__name__)])
async def chuigen(app: GraiaMiraiApplication, group: Group, message: MessageChain, member:Member):
    if '根瘤菌' in message.asDisplay() and '催更' in message.asDisplay():
        global uid,dy_type
        last = await get_thing(uid, 0)
        last_video = await get_thing(uid, 1, '8')
        await app.sendGroupMessage(group, MessageChain.create([
            Plain(text = '根瘤菌已经\n'),
            Plain(text = str(datetime.datetime.now()-datetime.datetime.fromtimestamp(last)).replace('days, ','天').replace('day, ','天')),
            Plain(text = '没有动静\n'),
            Plain(text = str(datetime.datetime.now()-datetime.datetime.fromtimestamp(last_video)).replace('days, ','天').replace('day, ','天')),
            Plain(text = '没有更新视频')
            ]))

async def get_thing(uid,dyn_,dyn_type=None):
    st_url = r"https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history?host_uid="+str(uid)
    url=st_url
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) ' \
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
    all_type={}

    while True:
        async with aiohttp.request("GET",url,headers = headers)as r:
            resp = await r.json()
        if resp['data']['cards'][0]['extra']['is_space_top'] == 1:
            cards=resp['data']['cards'][1:]
        elif resp['data']['cards'][0]['extra']['is_space_top'] == 0:
            cards=resp['data']['cards']

        if dyn_ == 0:
            return cards[0]['desc']['timestamp']
        else:
            for dy in cards:
                if dy['desc']['type'] == int(dyn_type):
                    return dy['desc']['timestamp']

        if resp['data']['has_more'] == 0:
            return all_type
        else:
            url = st_url+"&offset_dynamic_id="+str(resp['data']['next_offset'])
