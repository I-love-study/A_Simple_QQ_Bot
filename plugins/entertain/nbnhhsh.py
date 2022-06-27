import aiohttp
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import *
from graia.ariadne.message.parser.twilight import (FullMatch, MatchResult,
                                                   SpacePolicy, Twilight,
                                                   WildcardMatch)
from graia.ariadne.model import Group, Member
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

channel = Channel.current()

channel.name("nbnhhsh")
channel.description("发送'nbnhhsh [缩写]'返回缩写全程")
channel.author("I_love_study")
aiohttp.ClientSession
@channel.use(ListenerSchema(
    listening_events=[GroupMessage],
    inline_dispatchers=[Twilight(
        [FullMatch("nbnhhsh").space(SpacePolicy.FORCE),
         WildcardMatch(optional=True) @ "para"]
    )]
))
async def nbnhhsh(app: Ariadne, group: Group, para: MatchResult):
    if not para.matched:
        msg = '能不能好好说话'
    else:
        js = {'text': para.result.display.strip()}
        url = "https://lab.magiconch.com/api/nbnhhsh/guess"
        async with aiohttp.request("POST", url, json=js) as r:
            ret = (await r.json())[0]
        if (w := ret.get("trans")) and len(w):
            msg = f"缩写{ret['name']}的全称:\n" + '\n'.join(w)
        elif (w := ret.get("inputting")) and len(w):
            msg = f"缩写{ret['name']}的全称:\n" + '\n'.join(w)
        else:
            msg = f"没找到{ret['name']}的全称"
    
    await app.send_group_message(group, MessageChain(msg))