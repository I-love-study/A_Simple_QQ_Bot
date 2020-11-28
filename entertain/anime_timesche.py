from graia.application import GraiaMiraiApplication
from graia.application.event.messages import GroupMessage
from graia.application.message.elements.internal import Plain, At, Image
from graia.application.message.chain import MessageChain
from graia.application.message.parser.kanata import Kanata
from graia.application.message.parser.signature import RegexMatch
from graia.application.group import Group, Member
from graia.template import Template
from core import judge
from core import get

import aiohttp
import time
from PIL import Image as IMG
from PIL import ImageDraw, ImageFont
from io import BytesIO

__plugin_name__ = '番剧时刻表'
__plugin_usage__ = 'anime/anime tomorrow/anime yesterday'
bcc = get.bcc()
@bcc.receiver(GroupMessage, headless_decoraters = [judge.group_check(__name__)],
							dispatchers = [Kanata([RegexMatch('anime.*')])])
async def anime(app: GraiaMiraiApplication, group: Group, message: MessageChain, member: Member):
	tag = message.asDisplay().replace('anime','').strip()
	now_date = time.localtime()
	if tag == '':
		back = await get_anime_sche(f'{str(now_date.tm_mon).zfill(2)}-{now_date.tm_mday}')
	elif tag == 'yesterday':
		back = await get_anime_sche(f'{str(now_date.tm_mon).zfill(2)}-{now_date.tm_mday - 1}')
	elif tag == 'tomorrow':
		back = await get_anime_sche(f'{str(now_date.tm_mon).zfill(2)}-{now_date.tm_mday + 1}')
	else:
		await app.sendGroupMessage(group, Template('???').render())

	async with aiohttp.ClientSession() as session:
		n = 0
		final_back = IMG.new("RGB",(1200,300 * len(back)),(40,41,35))
		final_draw = ImageDraw.Draw(final_back)
		for single in back:
			async with session.get(single['square_cover']) as f:
				pic = IMG.open(BytesIO(await f.read()))
			if pic.size != (240, 240):
				pic = pic.resize((240, 240), IMG.ANTIALIAS)
			final_back.paste(pic, (30,30+300*n,270,270+300*n))
			
			ttf = ImageFont.truetype('C:/windows/fonts/SimHei.ttf', 60)
			ellipsis_size = ttf.getsize('...')[0]
			if ttf.getsize(single['title'])[0] >= 900:
				while ttf.getsize(single['title'])[0] > 900 - ellipsis_size:
					single['title'] = single['title'][:-1]
				single['title'] = single['title'] + '...'
			final_draw.text((300, 50+300*n), single['title'], font=ttf, fill=(255,255,255))
			final_draw.text((300, 150+300*n), single['pub_time'], font=ttf, fill=(255,255,255))
			final_draw.text((300+ttf.getsize(single['pub_time'])[0]+30, 150+300*n),
				single['pub_index'], font=ttf, fill=(0,160,216))
			n+=1
		out = BytesIO()
		final_back.save(out, format='JPEG')
	await app.sendGroupMessage(group, MessageChain.create([
		Image.fromUnsafeBytes(out.getvalue())]))



async def get_anime_sche(date):
	url = 'https://bangumi.bilibili.com/web_api/timeline_global'
	async with aiohttp.request("GET", url) as r:
		respone = await r.json()
	for date_anime in respone['result']:
		if date_anime['date'] == date:
			return date_anime['seasons']