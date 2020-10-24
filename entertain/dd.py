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
import itertools
import aiohttp

__plugin_name__ = 'Super DD'
__plugin_usage__ = '''/hololive [参数]
/花寄 或/花寄女子寮 或/花寄女生宿舍 [参数]
/Paryi的奇妙关系 或/帕里的奇妙关系 或/帕里全家福 [参数]
参数为video或live'''

headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                       'Chrome/81.0.4044.69 Safari/537.36 Edg/81.0.416.34'}

hololive_ids=[511613157, 511613155, 511613156, 491474050,
              491474049, 491474051, 491474048, 491474052,
              456368455, 444316844, 354411419, 427061218,
              454955503, 455172819, 454733056, 454737600,
              9034870, 443305053, 443300418, 389056211,
              412135619, 412135222, 366690056, 286179206,
              389856447, 339567211, 389862071, 389858027,
              332704117, 336731767, 389857131, 389857640,
              20813493, 389859190, 389858754, 375504219]

Hanayori_ids=[316381099,441403698,441381282,441382432]

paryi_hop_ids=[1576121,198297,18149131,372984197,
               349991143,8119834,2778044,3149619,
               2191383,6055289,380829248,1869304,
               1429475,406805563,2299184,435569969,
               407106379,401480763,442902274,10077023,
               452100632,386900246,98181,480432362,
               511613155,11073,282994]

bcc = get.bcc()
@bcc.receiver(GroupMessage, headless_decoraters = [Depend(judge.active_check_message)])
async def hololive(app: GraiaMiraiApplication, group: Group, message: MessageChain, member: Member):
    get = message.asDisplay().strip().split(' ')
    if get[0] == 'hololive':
        do = get[1] if len(get) == 2 else None
    else:
        return
    if do in ["live", "直播"]:
        await app.sendGroupMessage(group, Template('这行命令将要花费20+s的时间，请耐心等候').render())
        back,time = await live_status_send(hololive_ids,'没有Hololive成员直播')
    elif do in ["video", "视频"]:
        await app.sendGroupMessage(group, Template('这行命令将要花费10+s的时间，请耐心等候').render())
        back,time = await get_ids_videos(hololive_ids,'Hololive没有更新视频')
    else:
        await app.sendGroupMessage(group, Template('你倒是说视频还是直播啊').render())
        return
    await app.sendGroupMessage(group, Template(back).render())
    await app.sendGroupMessage(group, Template('共用时{}'.format(time)).render())

@bcc.receiver(GroupMessage, headless_decoraters = [Depend(judge.active_check_message)])
async def Hanayori(app: GraiaMiraiApplication, group: Group, message: MessageChain, member: Member):
    get = message.asDisplay().strip().split(' ')
    if get[0] in ['花寄','花寄女子寮','花寄女生宿舍']:
        do = get[1] if len(get) == 2 else None
    else:
        return
    if do in ["live", "直播"]:
        back,time = await live_status_send(Hanayori_ids,'没有花寄女子寮成员直播')
    elif do in ["video", "视频"]:
        back,time = await get_ids_videos(Hanayori_ids,'花寄女子寮没有更新视频')
    else:
        await app.sendGroupMessage(group, Template('你倒是说视频还是直播啊').render())
        return
    await app.sendGroupMessage(group, Template(back).render())
    await app.sendGroupMessage(group, Template('共用时{}'.format(time)).render())

@bcc.receiver(GroupMessage, headless_decoraters = [Depend(judge.active_check_message)])
async def amazing_paryi(app: GraiaMiraiApplication, group: Group, message: MessageChain, member: Member):
    get = message.asDisplay().strip().split(' ')
    if get[0] in ['Paryi的奇妙关系','帕里的奇妙关系','帕里全家福']:
        do = get[1] if len(get) == 2 else None
    else:
        return
    if do in ["live", "直播"]:
        await app.sendGroupMessage(group, Template('这行命令将要花费15+s的时间，请耐心等候').render())
        back,time = await live_status_send(paryi_hop_ids,'Paryi家啥也没干，淦')
    elif do in ["video", "视频"]:
        await app.sendGroupMessage(group, Template('这行命令将要花费10+s的时间，请耐心等候').render())
        back,time = await get_ids_videos(paryi_hop_ids,'Paryi家视频也没有啊')
    else:
        await app.sendGroupMessage(group, Template('你倒是说视频还是直播啊').render())
        return
    await app.sendGroupMessage(group, Template(back).render())
    await app.sendGroupMessage(group, Template('共用时{}'.format(time)).render())

async def live_status_send(ids,none_send):
    start=time.time()
    send=""
    for bilibili_id in ids:
        get = await get_live_status(bilibili_id)
        if get == None:
            continue
        if get['status'] == 1:
            send+= '\n'+get['uname']+'\n'+\
                   get['title']+'\n'+get['url']+\
                   '\n开播时间：\n'+get['start']+'\n'
    if send == "":
        return [none_send,time.time()-start]
    else:
        return ['正在直播的有：\n'+send,time.time()-start]
async def get_live_status(bilibili_id):
    live_api="http://api.live.bilibili.com/bili/living_v2/"
    status_api="https://api.live.bilibili.com/xlive/web-room/v1/index/getInfoByRoom?room_id="
    live=live_api+str(bilibili_id)
    async with aiohttp.request("GET",live,headers=headers)as r:
        live_id=await r.json()
        live_id=live_id['data']['url'].split(r'/')[-1]
        if live_id=="":
            return
        status=status_api+live_id
    async with aiohttp.request("GET",status,headers=headers)as r:
        info=await r.json()
        try:
            start_utc=int(info['data']['room_info']['live_start_time'])
        except Exception:
            return
        start_time= time.strftime("%Y.%m.%d %H:%M:%S", time.localtime(start_utc))
        use={}
        use['status']=info['data']['room_info']['live_status']
        use['uname']=info['data']['anchor_info']['base_info']['uname']
        use['title']=info['data']['room_info']['title']
        use['start']=start_time
        use['url']='https://live.bilibili.com/'+live_id
        return use
async def get_ids_videos(ids,none_send):
    start=time.time()
    send=""
    videos=[]
    for bilibili_id in ids:
        get = await get_video(bilibili_id,10)
        videos.extend(get)
    videos.sort()
    revideos=list(k for k,_ in itertools.groupby(videos))
    sorted(revideos,key=lambda revideo:revideo[0])
    use_time=int(time.time())-6*60*60
    videos=[video for video in revideos if video[0] >= use_time]
    for video in videos:
        play_time= time.strftime("%Y.%m.%d %H:%M:%S", time.localtime(video[0]))
        if video[5] == 1:
            video[1]+=' 等'
        send+='\n'+video[1]+'\n'+video[2]+'\nhttps://www.bilibili.com/video/av'+str(video[3])+'\n发布时间:'+play_time+'\n'
    if send == "":
        return [none_send,time.time()-start]
    else:
        return ['近6小时视频：\n'+send,time.time()-start]   
async def get_video(bilibili_id,ps):
    play=[]
    url="https://api.bilibili.com/x/space/arc/search?mid={}&pn=1&ps={}&jsonp=jsonp".format(bilibili_id,ps)
    async with aiohttp.request("GET",url,headers=headers) as r:
        reponse = await r.json()
        videos=reponse['data']['list']['vlist']
        for video in videos:
            v_list=[video['created'],video['author'],video['title'],
                    video['aid'],video['mid'],video['is_union_video']]#aid为视频mid为人
            play.append(v_list)
        return play