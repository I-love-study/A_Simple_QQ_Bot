from graia.broadcast.builtin.decoraters import Depend
from graia.application import GraiaMiraiApplication
from graia.application.event.messages import GroupMessage
from graia.application.message.elements.internal import Plain, At, Image
from graia.application.message.chain import MessageChain
from graia.application.message.parser.kanata import Kanata
from graia.application.message.parser.signature import FullMatch, RequireParam
from graia.application.group import Group, Member
from graia.template import Template
from expand import judge
from core import get
import time, urllib
from lxml import etree
import aiohttp
import asyncio
import yaml
from pathlib import Path

__plugin_name__ = 'Super DD'
__plugin_usage__ = '''/hololive [参数]
/花寄 或/花寄女子寮 或/花寄女生宿舍 [参数]
/Paryi的奇妙关系 或/帕里的奇妙关系 或/帕里全家福 [参数]
参数为video或live'''

headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                       'Chrome/81.0.4044.69 Safari/537.36 Edg/81.0.416.34'}


with open(Path(__file__).parent / 'dd_info.yml', 'r', encoding = 'UTF-8') as f:
    dd_data = yaml.safe_load(f.read())

bcc = get.bcc()

@bcc.receiver(GroupMessage, headless_decoraters = [Depend(judge.active_check_message)])
async def hololive(app: GraiaMiraiApplication, group: Group, message: MessageChain, member: Member):
    get = message.asDisplay().strip().split(' ')
    if get[0] == 'hololive':
        do = get[1] if len(get) == 2 else None
    else:
        return
    if do in ["live", "直播"]:
        status = await live_status_send(dd_data['Hololive']['room_id'])
        mes = MessageChain.create(status if status else [Plain('没有Hololive成员直播')])
    elif do in ["video", "视频"]:
        status = await get_ids_videos(dd_data['Hololive']['mid'])
        mes = MessageChain.create(status if status else [Plain('Hololive成员没有更新视频')])
    else:
        mes = Template('你倒是说视频还是直播啊kora').render()
    try:
        await app.sendGroupMessage(group, mes)
    except Exception:
        await app.sendGroupMessage(group, MessageChain.create([Plain('Oops,出现了点问题导致信息无法发送')]))

@bcc.receiver(GroupMessage, headless_decoraters = [Depend(judge.active_check_message)])
async def Hanayori(app: GraiaMiraiApplication, group: Group, message: MessageChain, member: Member):
    get = message.asDisplay().strip().split(' ')
    if get[0] in ['花寄','花寄女子寮','花寄女生宿舍']:
        do = get[1] if len(get) == 2 else None
    else:
        return
    if do in ["live", "直播"]:
        status = await live_status_send(dd_data['Hanayori']['room_id'])
        mes = MessageChain.create(status if status else [Plain('没有花寄女子寮成员直播')])
    elif do in ["video", "视频"]:
        status = await get_ids_videos(dd_data['Hanayori']['mid'])
        mes = MessageChain.create(status if status else [Plain('花寄女子寮成员没有更新视频')])
    else:
        mes = Template('你倒是说视频还是直播啊kora').render()
    try:
        await app.sendGroupMessage(group, mes)
    except Exception:
        await app.sendGroupMessage(group, MessageChain.create([Plain('Oops,出现了点问题导致信息无法发送')]))

@bcc.receiver(GroupMessage, headless_decoraters = [Depend(judge.active_check_message)])
async def amazing_paryi(app: GraiaMiraiApplication, group: Group, message: MessageChain, member: Member):
    get = message.asDisplay().strip().split(' ')
    if get[0] in ['Paryi的奇妙关系','帕里的奇妙关系','帕里全家福']:
        do = get[1] if len(get) == 2 else None
    else:
        return
    if do in ["live", "直播"]:
        status = await get_lives(dd_data['Paryi_hop']['room_id'])
        mes = MessageChain.create(status if status else [Plain('Paryi家啥也没干，淦')])
    elif do in ["video", "视频"]:
        status = await get_videos(dd_data['Paryi_hop']['mid'])
        mes = MessageChain.create(status if status else [Plain('Paryi家视频也没有啊')])
    else:
        mes = Template('你倒是说视频还是直播啊').render()
    try:
        await app.sendGroupMessage(group, mes)
    except Exception:
        await app.sendGroupMessage(group, MessageChain.create([Plain('Oops,出现了点问题导致信息无法发送')]))

async def get_lives(ids):
    status_api = "https://api.live.bilibili.com/xlive/web-room/v1/index/getInfoByRoom?room_id="
    conn = aiohttp.TCPConnector(limit = 5)
    async with aiohttp.ClientSession(connector = conn) as session:
        tasks = [fench(session, status_api + str(live_id)) for live_id in ids]
        lives = await asyncio.gather(*tasks)
    if lives:
        send = [Plain('正在直播的有:')]
        for live in lives:
            if live['data']['room_info']['live_status'] == 1:
                start_time = live['data']['room_info']['live_start_time']
                send.extend([Plain(f"\n{live['data']['anchor_info']['base_info']['uname']}"),
                             Plain(f"\n{live['data']['room_info']['title']}"),
                             Plain(f"\nhttps://live.bilibili.com/{live['data']['room_info']['room_id']}"),
                             Plain(f"\n开播时间："),
                             Plain(f"\n{time.strftime('%Y.%m.%d %H:%M:%S',time.gmtime(start_time))}"),
                            ])
        return send

async def get_videos(ids):
    url = "https://api.bilibili.com/x/space/arc/search?mid={mid}&pn=1&ps={ps}&jsonp=jsonp"
    conn = aiohttp.TCPConnector(limit = 5)
    async with aiohttp.ClientSession(connector = conn) as session:
        tasks = [fench(session, url.format(mid = mid, ps = 10)) for mid in ids]
        user_videos = await asyncio.gather(*tasks)
    videos = [video for videos in user_videos for video in videos['data']['list']['vlist']]
    videos = [video for video in videos if video['created'] >= int(time.time())-6*60*60]
    videos = sorted(videos, key = lambda videos:videos['created'])
    if videos:
        for video in videos:
            send = [Plain('近6小时视频：\n')]
            play_time = time.strftime("%Y.%m.%d %H:%M:%S", time.gmtime(video['created']))
            send.extend([Plain(f"\n{video['author']}{'等' if video['is_union_video'] else ''}"),
                         Plain(f"\n{video['title']}"),
                         Plain(f"\nhttps://www.bilibili.com/video/av{video['aid']}"),
                         Plain(f"\n发布时间:{play_time}\n")
                        ]) 
        return send

async def get_video(bilibili_id, ps):
    url="https://api.bilibili.com/x/space/arc/search?mid={}&pn=1&ps={}&jsonp=jsonp".format(bilibili_id,ps)
    async with aiohttp.request("GET",url,headers=headers) as r:
        reponse = await r.json()
        return reponse['data']['list']['vlist']

async def fench(session, url, **kwargs):
    async with session.get(url, **kwargs) as r:
        return await r.json()