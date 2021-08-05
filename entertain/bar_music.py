from graia.application import GraiaMiraiApplication
from graia.application.event.messages import GroupMessage
from graia.application.message.elements.internal import *
from graia.application.message.chain import MessageChain
from graia.application.message.parser.kanata import Kanata
from graia.application.message.parser.signature import FullMatch, RequireParam
from graia.application.group import Group, Member
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.template import Template
from graiax import silkcoder
from expand import Netease

import platform

channel = Channel.current()

channel.name("BarMusic")
channel.description("发送'bar_music [歌曲名]'获取语音音乐")
channel.author("I_love_study")

@channel.use(ListenerSchema(
	listening_events=[GroupMessage],
	inline_dispatchers=[Kanata([FullMatch('bar_music'), RequireParam(name = 'tag')])]
	))
async def bar_music(app: GraiaMiraiApplication, group: Group, member: Member, tag: MessageChain):
	if tag.asDisplay().strip() == '':
		await app.sendGroupMessage(group, Template('点啥歌？').render())
		return
	search_data = await Netease.search(tag.asDisplay().strip())
	try:
		download = await Netease.download_song(search_data[0]['id'])
	except Exception:
		await app.sendGroupMessage(group, Template('不知道为什么，但是我就是放不了').render())
		return
	if platform.system() == "Windows":
		cache = Path(r"E:\python\QQ,Wechat\python-mirai\mcl\data\net.mamoe.mirai-api-http\voices\cache")
	else: #服务器
		cache = Path(r"\root\bot\mcl\data\net.mamoe.mirai-api-http\voices\cache")
	cache.write_bytes(await silkcoder.encode(download, rate=80000, ss=0, t=60))
	await app.sendGroupMessage(group, MessageChain.create([Voice(path="cache")]))