from graia.application import GraiaMiraiApplication
from graia.application.event.messages import GroupMessage
from graia.application.message.elements.internal import *
from graia.application.message.chain import MessageChain
from graia.application.message.parser.kanata import Kanata
from graia.application.message.parser.signature import FullMatch, RequireParam
from graia.application.group import Group, Member
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

import time
from io import BytesIO
import aiohttp
import asyncio
import yaml
from pathlib import Path
from PIL import Image as IMG
from itertools import product
from operator import itemgetter
import math

headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                       'Chrome/81.0.4044.69 Safari/537.36 Edg/81.0.416.34'}

channel = Channel.current()

channel.name("DDSystem")
channel.description('''输入 '直播 [Hololive/Hanayori/Paryi_hop]'
或者 监控室 [Hololive/Hanayori/Paryi_hop]''')
channel.author("I_love_study")

@channel.use(ListenerSchema(
    listening_events=[GroupMessage],
    inline_dispatchers=[Kanata([FullMatch('直播 '), RequireParam('tag')])]
    ))
async def dd_watch(app: GraiaMiraiApplication, group: Group, member: Member, tag: MessageChain):
    dd_data = yaml.safe_load((Path(__file__).parent/'dd_info.yml').read_text(encoding = 'UTF-8'))
    name = tag.asDisplay().strip()
    if name not in dd_data:
        await app.sendGroupMessage(group, MessageChain.create([Plain('未发现你要D的组织')]))
        return
    status_api = "https://api.live.bilibili.com/xlive/web-room/v1/index/getInfoByRoom?room_id="
    conn = aiohttp.TCPConnector(limit = 5)#防爆毙
    async with aiohttp.ClientSession(connector = conn) as session:
        tasks = [fench(session, f'{status_api}{live_id}') for live_id in dd_data[name]['room_id']]
        lives = await asyncio.gather(*tasks)
        send = []
    for live in lives:
        if live['data']['room_info']['live_status'] == 1:
            start_time = live['data']['room_info']['live_start_time']
            send.extend([
                Plain(f"\n{live['data']['anchor_info']['base_info']['uname']}"),
                Plain(f"\n{live['data']['room_info']['title']}"),
                Plain(f"\nhttps://live.bilibili.com/{live['data']['room_info']['room_id']}"),
                Plain(f"\n开播时间："),
                Plain(f"\n{time.strftime('%Y.%m.%d %H:%M:%S',time.gmtime(start_time))}"),
                ])
    mes = MessageChain.create([Plain('正在直播的有:'),*send] if send else [Plain(f'没有{name}成员直播')])
    await app.sendGroupMessage(group, mes)

@channel.use(ListenerSchema(
    listening_events=[GroupMessage],
    inline_dispatchers=[Kanata([FullMatch('监控室 '), RequireParam('tag')])]
    ))
async def dd_monitor(app: GraiaMiraiApplication, group: Group, member: Member, tag: MessageChain):
    dd_data = yaml.safe_load((Path(__file__).parent/'dd_info.yml').read_text(encoding = 'UTF-8'))
    if name := tag.asDisplay().strip() not in dd_data:
        await app.sendGroupMessage(group, MessageChain.create([Plain('未发现你要D的组织')]))
        return
    status_api = "https://api.live.bilibili.com/xlive/web-room/v1/index/getInfoByRoom?room_id="
    conn = aiohttp.TCPConnector(limit = 5)#防爆毙
    async with aiohttp.ClientSession(connector = conn) as session:
        tasks = [fench(session, f'{status_api}{live_id}') for live_id in dd_data[name]['room_id']]
        lives = await asyncio.gather(*tasks)
        tasks = [fench(session, live['data']['room_info']['keyframe'], ret='read')
                for live in lives if live['data']['room_info']['live_status'] == 1]
        if tasks:
            pics_data = await asyncio.gather(*tasks)
        else:
            await app.sendGroupMessage(group, MessageChain.create([Plain(f'没有{name}成员直播')]))
            return

    frame = int(math.ceil(len(pics_data)**0.5))
    frame = (frame, int(math.ceil(len(pics_data)/frame)))
    final_back = IMG.new("RGB", (1280*frame[0], 720*frame[1]), (0,0,0))
    length = len(pics_data)
    for h, w in product(range(frame[0]),range(frame[1])):
        if (n := frame[1]*h+w) < length:
            pic = IMG.open(BytesIO(pics_data[n]))
            if pic.size != (1280, 720):
                pic = pic.resize((1280, 720), IMG.ANTIALIAS)
            final_back.paste(pic, (1280*w,720*h))
        else:
            break
    out = BytesIO()
    final_back.save(out, format='JPEG', quality = 80)
    await app.sendGroupMessage(group, MessageChain.create([
        Image.fromUnsafeBytes(out.getvalue())]))

@channel.use(ListenerSchema(
    listening_events=[GroupMessage],
    inline_dispatchers=[Kanata([FullMatch('视频 '), RequireParam('tag')])]
    ))
async def dd_video(app: GraiaMiraiApplication, group: Group, member: Member, tag: MessageChain):
    dd_data = yaml.safe_load((Path(__file__).parent/'dd_info.yml').read_text(encoding = 'UTF-8'))
    name = tag.asDisplay().strip()
    if name not in dd_data:
        await app.sendGroupMessage(group, MessageChain.create([Plain('未发现你要D的组织')]))
        return
    conn = aiohttp.TCPConnector(limit = 5)#防爆毙
    async with aiohttp.ClientSession(connector = conn) as session:
        tasks = [get_videos(session, mid, 6*60*60) for mid in dd_data[name]['mid']]
        user_videos = await asyncio.gather(*tasks)
    user_videos = [video for videos in user_videos for video in videos]
    if user_videos:
        send = [Plain('近6小时视频：\n')]
        user_videos.sort(key = itemgetter('created'))
        for video in user_videos:
            play_time = time.strftime("%Y.%m.%d %H:%M:%S", time.gmtime(video['created']))
            send.extend([Plain(f"\n{video['author']}{'等' if video['is_union_video'] else ''}"),
                         Plain(f"\n{video['title']}"),
                         Plain(f"\nhttps://www.bilibili.com/video/av{video['aid']}"),
                         Plain(f"\n发布时间:{play_time}\n")
                        ])
        await app.sendGroupMessage(group, MessageChain.create(send))
    else:
        await app.sendGroupMessage(group, MessageChain.create([Plain('好家伙,他们一个也没更新')]))

async def get_videos(session, mid, last_time):
    n = 1
    url = "https://api.bilibili.com/x/space/arc/search?mid={mid}&pn={n}&ps=10&jsonp=jsonp"
    ret = []
    while True:
        async with session.get(url.format(mid=mid, n=n)) as r:
            js = await r.json()
        for video in js['data']['list']['vlist']:
            if video['created'] >= int(time.time())-last_time:
                ret.append(video)
            elif video['is_union_video']:
                break
            n+=1
    return ret

async def fench(session, url, ret = 'json', **kwargs):
    async with session.get(url, **kwargs) as r:
        if ret == 'json':
            return await r.json()
        elif ret == 'read':
            return await r.read()