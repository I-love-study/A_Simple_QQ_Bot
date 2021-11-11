from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import *
from graia.ariadne.message.parser.pattern import FullMatch, RegexMatch
from graia.ariadne.message.parser.twilight import Sparkle, Twilight
from graia.ariadne.model import Group, Member
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

import aiohttp

channel = Channel.current()
channel.name("HotwordSearch")
channel.description("获取热词解释")
channel.author("I_love_study")

class Sp(Sparkle):
    para = RegexMatch(".*")
    end = FullMatch("是什么梗")

@channel.use(ListenerSchema(
    listening_events=[GroupMessage],
    inline_dispatchers=[Twilight(Sp)]
))
async def hotword(app:Ariadne, group: Group, sparkle: Sparkle):
    url = "https://api.jikipedia.com/go/search_definitions"
    headers = {"Client": "web", "Content-Type": "application/json;charset=UTF-8"}
    payload = {"phrase": sparkle.para.result.asDisplay(), "page": 1}
    async with aiohttp.request("POST", url, headers=headers, json=payload) as r:
        result = (await r.json())["data"][0]
    
    await app.sendGroupMessage(group, MessageChain.create([
        Plain(text=f"{result['term']['title']}\n\n"),
        Plain(text=f"标签：{' '.join(tag['name'] for tag in result['tags'])}\n"),
        Plain(text="释义：\n" + result['plaintext'])
    ]))