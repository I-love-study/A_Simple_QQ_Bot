from graia.application import GraiaMiraiApplication
from graia.application.event.messages import GroupMessage
from graia.application.message.elements.internal import *
from graia.application.message.chain import MessageChain
from graia.application.message.parser.kanata import Kanata
from graia.application.message.parser.signature import FullMatch, RequireParam
from graia.application.group import Group, Member
from graia.template import Template
from expand import Netease
from expand import transcode
from core import judge
from core import get

__plugin_name__ = '语音听歌'
__plugin_usage__ = 'bar_music [歌曲名字]'

bcc = get.bcc()
@bcc.receiver(GroupMessage, headless_decoraters = [judge.group_check(__name__)],
							dispatchers = [Kanata([FullMatch('bar_music'), RequireParam(name = 'tag')])])
async def bar_music(app: GraiaMiraiApplication, group: Group, message: MessageChain, member: Member, tag: MessageChain):
	if tag.asDisplay().strip() == '':
		await app.sendGroupMessage(group, Template('点啥歌？').render())
		return
	search_data = await Netease.search(tag.asDisplay().strip())
	try:
		download = await Netease.download_song(search_data[0]['id'])
	except Exception as e:
		print(e)
		await app.sendGroupMessage(group, Template('不知道为什么，但是我就是放不了').render())
		return
	music_b = await transcode.silk(download, 'b', '-ss 0 -t 60')
	await app.sendGroupMessage(group, MessageChain.create([await app.uploadVoice(music_b)]))

