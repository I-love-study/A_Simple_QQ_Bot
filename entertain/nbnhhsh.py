from graia.application import GraiaMiraiApplication
from graia.application.event.messages import GroupMessage
from graia.application.message.elements.internal import *
from graia.application.message.chain import MessageChain
from graia.application.message.parser.kanata import Kanata
from graia.application.message.parser.signature import FullMatch, OptionalParam
from graia.application.group import Group, Member
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

import aiohttp

channel = Channel.current()

channel.name("nbnhhsh")
channel.description("发送'nbnhhsh [缩写]'返回缩写全程")
channel.author("I_love_study")

@channel.use(ListenerSchema(
    listening_events=[GroupMessage],
    inline_dispatchers=[Kanata([FullMatch('nbnhhsh'), OptionalParam('params')])]))
async def nbnhhsh(app: GraiaMiraiApplication, group: Group, params):
    if params is None:
        msg = '能不能好好说话'
    else:
        js = {'text': params.asDisplay().strip()}
        url = "https://lab.magiconch.com/api/nbnhhsh/guess"
        async with aiohttp.request("POST", url, json=js) as r:
            ret = (await r.json())[0]
        if ret['trans']:
            msg = f"缩写{ret['name']}的全称:\n" + '\n'.join(ret['trans'])
        else:
            msg = f"没找到{ret['name']}的全称"
    
    await app.sendGroupMessage(group, MessageChain.create([
        Plain(msg)
    ]))