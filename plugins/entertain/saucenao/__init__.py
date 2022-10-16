from datetime import datetime

from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, Source, Forward, ForwardNode
from graia.ariadne.message.parser.twilight import Twilight, FullMatch, ElementMatch, ElementResult
from graia.ariadne.model import Group, Member
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from .saucenao import SauceNao
from .exception import SauceNaoApiError

channel = Channel.current()

channel.name("Saucenao")
channel.description("以图搜图")
channel.author("I_love_study")

apikey = "a866874836003a8f43ad58ce499776d8d326169a"

# 其他代码来源于 saucenao-api

@channel.use(
    ListenerSchema(listening_events=[GroupMessage],
                   inline_dispatchers=[
                       Twilight([
                           FullMatch("以图搜番"),
                           FullMatch("\n", optional=True),
                           "img" @ ElementMatch(Image, optional=True),
                       ]),
                   ]))
async def saucenao(app: Ariadne, group: Group, member: Member, img: ElementResult, source: Source):
    assert isinstance(img.result, Image)
    image_url = img.result.url
    assert image_url

    await app.send_group_message(group, MessageChain("正在搜索，请稍后"), quote=source.id)
    async with SauceNao(apikey, numres=3) as snao:
        try:
            results = await snao.from_url(image_url)
        except SauceNaoApiError as e:
            await app.send_message(group, MessageChain("搜索失败desu"))
            return

    fwd_node_list = []
    for results in results.results:
        if len(results.urls) == 0:
            continue
        urls = "\n".join(results.urls)
        fwd_node_list.append(
            ForwardNode(
                target=app.account,
                sender_name="爷",
                time=datetime.now(),
                message=MessageChain(
                    f"相似度：{results.similarity}%\n标题：{results.title}\n节点名：{results.index_name}\n链接：{urls}"
                )))

    if not fwd_node_list:
        await app.send_message(group, MessageChain("未找到有价值的数据"), quote=source.id)
    else:
        await app.send_message(group, MessageChain(Forward(node_list=fwd_node_list)))
    