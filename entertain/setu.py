from graia.broadcast.builtin.decoraters import Depend
from graia.application import GraiaMiraiApplication
from graia.application.event.messages import GroupMessage
from graia.application.message.elements.internal import Plain, At, Image, Source
from graia.application.message.chain import MessageChain
from graia.application.message.parser.kanata import Kanata
from graia.application.message.parser.signature import FullMatch, RequireParam
from graia.application.group import Group, Member, MemberPerm
from graia.template import Template
from expand import judge
from core import get

import random
import asyncio
import aiohttp
import aiofiles
import datetime
import time
import ujson as json
from pathlib import Path

__plugin_name__ = '涩图来'
__plugin_usage__ = '都是lsp了，都知道怎么用了'

call = {}
for g in get.trans('active_groups'):
    call[g] = []

pixiv_headers = {
    'Referer': 'https://www.pixiv.net/member_illust.php?mode=medium&illust_id',
    'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
    }

bcc = get.bcc()
@bcc.receiver(GroupMessage, headless_decoraters = [Depend(judge.active_check_message)],
							dispatchers = [Kanata([FullMatch('涩图来')])])
async def setu(app: GraiaMiraiApplication, group: Group, message: MessageChain, member: Member):
    if not config['power']:
        await app.sendGroupMessage(group, Template('打烊了').render())
        return

    d_time = datetime.datetime.fromisoformat(str(datetime.date.today())+'T06:30')
    d_time1 =  datetime.datetime.fromisoformat(str(datetime.date.today())+'T23:00')
    n_time = datetime.datetime.now()
    if not d_time <= n_time <= d_time1 or config['overtime']:
    	await app.sendGroupMessage(group, Template('爬，我要睡觉').render())
    	return

    before = time.time() - config['per']
    call[group.id] = [d for d in call[group.id] if d['time'] >= before]

    if call[group.id] >= config['global_speed']:
        await app.sendGroupMessage(group, Template('你们都太快了，不要冲坏了身体').render())

    q_ids = [single['q_id'] for single in call[group.id]]
    count = dict([(q_id, q_ids.count(q_id)) for q_id in set(q_ids)])
    if count[member.id] >= config['user_speed']:
        await app.sendGroupMessage(group, Template('你太快了，不要冲坏了身体').render())
        return

    call[group.id].append({'q_id': member.id, 'time':time.time()})

    if len(parmas := message.asDisplay().replace('涩图来', '').strip().split(' ', 2)) == 2:
        command, value = parmas
    elif param == 1:
        command = param
        value = None
    else:
        command = None
        value = None

    if config['ero_from'] == 'local':
        x = 1
        if command == 'tag':
            await app.sendGroupMessage(group, Template('本地涩图哪来的tag啊kora').render(), quote = message.get(Source)[0])
            return
        elif re.fullmatch('/*[0-9]+', command):
            x = int(command.replace('*', ''))
            if x == 0:
                await app.sendGroupMessage(group, Template('哦').render(), quote = message.get(Source)[0])
                return
            elif x >= config['ero_max']:
                await app.sendGroupMessage(group, Template('要这么多涩图的屑').render(), quote = message.get(Source)[0])
        send = random.sample(list(Path('setu').iterdir()), 1)[0]
        m = await app.sendGroupMessage(group, MessageChain.create([Image.fromLocalFile(send)]))
    elif config['ero_from'] == 'web'
        parmas = {'apikey' : '829821985f6de98edb9224', 'r18' : 0, 'proxy' : 'disable', 'size1200' : 'true'}
        if command == 'tag' and value:
            parmas['keyword'] = tag
        elif re.fullmatch('/*[0-9]*', command):
            await app.sendGroupMessage(group, MessageChain.create([
                Plain('我很可爱,请给我钱\n买出国机票,返好看涩图')
                ]), quote = message.get(Source)[0])

        async with aiohttp.request("GET",url = 'https://api.lolicon.app/setu/', params = parmas) as r:
            j_setu = await r.json()

        if j_setu['code'] == 429:
            await app.sendGroupMessage(group, Template('玛德你们这群lsp调用次数全™用完了').render())
            return
        if not j_setu['data']:
            await app.sendGroupMessage(group, MessageChain.create([
                At(target = member.id),
                Plain(text = '没搜索到相关色图'),
                Plain(text = f"\n剩余调用次数:{j_setu['quota']}")]))
            return

        async with aiohttp.request("GET", url = j_setu['data'][0]['url'], headers = pixiv_headers) as r:
            setu = await r.read()
        send = await app.sendGroupMessage(group, MessageChain.create([
            At(target = member.id),
            Plain(text = '\n您要的涩图'),
            Plain(text = f"\npid:{n_setu['pid']}"),
            Plain(text = f"\n{n_setu['title']}/{n_setu['author']}"),
            Plain(text = f"\n剩余调用次数:{j_setu['quota']}"),
            Image.fromUnsafeBytes(setu)
            ]), quote = message.get(Source)[0])

    if config['revoke']:
        await asyncio.sleep(config['revoke'])
        await app.revokeMessage(target = m)

with open(r'config.json', 'r', encoding = 'UTF-8') as f:
    config = json.load(f)

def admin_judge(member: Member):
    if member.id not in [1450069615] or member.permission != MemberPerm.Owner:
        raise ExecutionStop()

@bcc.receiver(GroupMessage, headless_decoraters = [Depend(judge.active_check_message), Depend(admin_judge)],
                            dispatchers = [Kanata([FullMatch('涩图set'), RequireParam(name = tag)])])
async def setuset(app: GraiaMiraiApplication, group: Group, message: MessageChain, member: Member, tag: MessageChain):
    if len(params := tag.asDisplay().strip().split(' ', 2)) == 2:
        command, value = parmas
    elif param == 1:
        command = param
    else :
        await app.sendGroupMessage(group, Template('ERROR').render())

    if command == 'info':
        await app.sendGroupMessage(group, MessageChain.create([
            Plain('现在设置为：'),
            Plain(f"\n功能启动：{('否','是')[config['power']]}"),
            Plain(f"\n加班模式：{('关','开')[config['power']]}"),
            Plain(f"\n涩图来源：{config['ero_from']}"),
            Plain(f"\n群单位时间最大涩图数：{config['global_speed']}"),
            Plain(f"\n用户单位时间最大涩图数：{config['user_speed']}"),
            Plain(f"\n单位时间：{config['per']}s")
            ]))
    elif command == 'power':
        if value == 'on':
            config['power'] = True
            await config_update()
            await app.sendGroupMessage(group, Template('涩图功能已启动').render())
        elif value == 'off':
            config['power'] = False
            await config_update()
            await app.sendGroupMessage(group, Template('涩图功能已关闭').render())
        else:
            await app.sendGroupMessage(group, Template('未知参数').render())
    elif command == 'overtime':
        if value == 'on':
            config['overtime'] = True
            await config_update()
            await app.sendGroupMessage(group, Template('加班功能已启动').render())
        elif value == 'off':
            config['overtime'] = False
            await config_update()
            await app.sendGroupMessage(group, Template('加班功能已关闭').render())
        else:
            await app.sendGroupMessage(group, Template('未知参数').render())
    elif command == 'erotype':
        if value == 'web':
            config['ero_from'] = 'web'
            await config_update()
            await app.sendGroupMessage(group, Template('开始使用网络涩图').render())
        elif value == 'local':
            config['ero_from'] = 'local'
            await config_update()
            await app.sendGroupMessage(group, Template('开始使用本地涩图').render())
        else:
            await app.sendGroupMessage(group, Template('未知参数').render())
    elif command == 'global':
        try:
            config['global_speed'] = int(value)
        except ValueError:
            await app.sendGroupMessage(group, Template('兄啊你倒是输个数字啊').render())
            return
        await config_update()
        await app.sendGroupMessage(group, Template('全群频率已修改').render())
    elif command == 'user':
        try:
            config['user_speed'] = int(value)
        except ValueError:
            await app.sendGroupMessage(group, Template('兄啊你倒是输个数字啊').render())
            return
        await config_update()
        await app.sendGroupMessage(group, Template('用户频率已修改').render())
    elif command == 'per':
        try:
            config['per'] = int(value)
        except ValueError:
            await app.sendGroupMessage(group, Template('兄啊你倒是输个数字啊').render())
            return
        await config_update()
        await app.sendGroupMessage(group, Template('恢复时间已修改').render())
    elif command == 'revoke':
        try:
            config['per'] = int(value)
        except ValueError:
            await app.sendGroupMessage(group, Template('兄啊你倒是输个数字啊').render())
            return
        await config_update()
        await app.sendGroupMessage(group, Template('撤回时间已修改').render())
    elif command == 'max':
        try:
            config['ero_max'] = int(value)
        except ValueError:
            await app.sendGroupMessage(group, Template('兄啊你倒是输个数字啊').render())
            return
        await config_update()
        await app.sendGroupMessage(group, Template('最大涩图调用已修改（仅本地生效）').render())

    else:
        await app.sendGroupMessage(group, Template('未知命令').render())

    async def config_update():
        async with aiofiles.open('config.json', 'w', encoding = 'UTF-8') as f:
            await f.write(json.dumps(config))