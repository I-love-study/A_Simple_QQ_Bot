from graia.application import GraiaMiraiApplication
from graia.application.event.messages import GroupMessage
from graia.application.message.elements.internal import Plain, At, Image
from graia.application.message.chain import MessageChain
from graia.application.message.parser.kanata import Kanata
from graia.application.message.parser.signature import FullMatch, RequireParam
from graia.application.group import Group, Member
from core import judge
from core import get

import aiohttp
import time

__plugin_name__ = '番剧时刻表'
__plugin_usage__ = 'anime/anime tomorrow/anime yesterday'
bcc = get.bcc()
@bcc.receiver(GroupMessage, headless_decoraters = [judge.group_check(__name__)],
							dispatchers = [Kanata([FullMatch('anime'), RequireParam(name = 'tag')])])
async def anime(app: GraiaMiraiApplication, group: Group, message: MessageChain, member: Member, tag: MessageChain):
	tag = tag.asDisplay().strip()
	now_date = time.localtime()
	print(f'{now_date.tm_mon}-{now_date.tm_mday}')
	if tag == '':
		back = await get_anime_sche(f'{str(now_date.tm_mon).zfill(2)}-{now_date.tm_mday}')
	elif tag == 'yesterday':
		back = await get_anime_sche(f'{str(now_date.tm_mon).zfill(2)}-{now_date.tm_mday - 1}')
	elif tag == 'tomorrow':
		back = await get_anime_sche(f'{str(now_date.tm_mon).zfill(2)}-{now_date.tm_mday + 1}')
	else:
		await app.sendGroupMessage(group, Template('???').render())

	mes = []
	for single in back:
		mes.extend([
			Image.fromNetworkAddress(single['square_cover']),
			Plain(single['title']),
			Plain(f"\n{single['pub_index']} {single['pub_time']}"	)
			])
	await app.sendGroupMessage(group, MessageChain.create(mes))



async def get_anime_sche(date):
	url = 'https://bangumi.bilibili.com/web_api/timeline_global'
	async with aiohttp.request("GET", url) as r:
		respone = await r.json()
	for date_anime in respone['result']:
		if date_anime['date'] == date:
			return date_anime['seasons']