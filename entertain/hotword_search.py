from graia.application import GraiaMiraiApplication
from graia.application.event.messages import GroupMessage
from graia.application.message.elements.internal import *
from graia.application.message.chain import MessageChain
from graia.application.message.parser.kanata import Kanata
from graia.application.message.parser.signature import FullMatch, RequireParam
from graia.application.group import Group, Member
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

import aiohttp

channel = Channel.current()
channel.name("HotwordSearch")
channel.description("获取热词解释")
channel.author("I_love_study")

@channel.use(ListenerSchema(
    listening_events=[GroupMessage],
    inline_dispatchers=[Kanata([RequireParam("tag"), FullMatch("是什么梗")])]
))
async def hotword(app:GraiaMiraiApplication, group: Group, member: Member, tag: MessageChain):
    url = "https://api.jikipedia.com/go/search_definitions"
    headers = {"Client": "web", "Content-Type": "application/json;charset=UTF-8"}
    payload = {"phrase": tag.asDisplay(), "page": 1}
    async with aiohttp.request("POST", url, headers=headers, json=payload) as r:
        result = (await r.json())["data"][0]
    
    await app.sendGroupMessage(group, MessageChain.create([
        Plain(text=f"{result['term']['title']}\n\n"),
        Plain(text=f"标签：{' '.join(tag['name'] for tag in result['tags'])}\n"),
        Plain(text="释义：\n" + result['plaintext'])
    ]))