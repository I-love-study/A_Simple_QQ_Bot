from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import *
from graia.ariadne.message.parser.pattern import FullMatch, WildcardMatch
from graia.ariadne.message.parser.twilight import Twilight
from graia.ariadne.model import Group, Member
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

import aiohttp

channel = Channel.current()

channel.name("nbnhhsh")
channel.description("发送'nbnhhsh [缩写]'返回缩写全程")
channel.author("I_love_study")

@channel.use(ListenerSchema(
    listening_events=[GroupMessage],
    inline_dispatchers=[Twilight(
        [FullMatch("nbnhhsh")], {"para": WildcardMatch(optional=True)}
    )]
))
async def nbnhhsh(app: Ariadne, group: Group, para: WildcardMatch):
    if not para.matched:
        msg = '能不能好好说话'
    else:
        js = {'text': para.result.asDisplay().strip()}
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