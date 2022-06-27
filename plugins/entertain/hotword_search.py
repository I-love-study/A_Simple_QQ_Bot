from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import *
from graia.ariadne.message.parser.base import DetectSuffix
from graia.ariadne.model import Group, Member
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

import aiohttp

channel = Channel.current()
channel.name("HotwordSearch")
channel.description("获取热词解释")
channel.author("I_love_study")

@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def hotword(app: Ariadne, group: Group, message: MessageChain = DetectSuffix("是什么梗")):
    url = "https://api.jikipedia.com/go/search_definitions"
    headers = {"Client": "web", "Content-Type": "application/json;charset=UTF-8"}
    payload = {"phrase": message.display, "page": 1}
    async with aiohttp.request("POST", url, headers=headers, json=payload) as r:
        result = (await r.json())["data"][0]

    await app.send_group_message(group, MessageChain([
        Plain(text=f"{result['term']['title']}\n\n"),
        Plain(text=f"标签：{' '.join(tag['name'] for tag in result['tags'])}\n"),
        Plain(text="释义：\n" + result['plaintext'])
    ]))