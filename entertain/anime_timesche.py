from graia.application import GraiaMiraiApplication
from graia.application.event.messages import GroupMessage
from graia.application.message.elements.internal import *
from graia.application.message.chain import MessageChain
from graia.application.message.parser.kanata import Kanata
from graia.application.message.parser.signature import FullMatch, OptionalParam
from graia.application.group import Group, Member
from core import judge
from core import get

import aiohttp
from datetime import date, datetime
from PIL import Image as IMG
from PIL import ImageDraw, ImageFont
from io import BytesIO

__plugin_name__ = '番剧时刻表'
__plugin_usage__ = 'anime/anime tomorrow/anime yesterday'
bcc = get.bcc()
@bcc.receiver(GroupMessage, headless_decoraters = [judge.config_check(__name__)],
							dispatchers = [Kanata([FullMatch('anime'), OptionalParam('para')])])
async def anime(app: GraiaMiraiApplication, group: Group, message: MessageChain, member: Member, para):
	today = int(datetime.fromisoformat(date.today().isoformat()).timestamp())
	date2ts = {'yesterday': today-86400, '':today, 'tomorrow': today+86400}
	d = para.asDisplay().strip() if isinstance(para, MessageChain) else ''

	if d in date2ts:
		date_ts = date2ts[d]
	else:
		await app.sendGroupMessage(group, MessageChain.create([Plain('未知时间')]))
		return

	async with aiohttp.ClientSession() as session:
		async with session.get('https://bangumi.bilibili.com/web_api/timeline_global') as r:
			result = (await r.json())['result']
			data = next(anime_ts['seasons'] for anime_ts in result if anime_ts['date_ts'] == date_ts)
		final_back = IMG.new("RGB",(1200,300 * len(data)),(40,41,35))
		final_draw = ImageDraw.Draw(final_back)
		for n, single in enumerate(data):
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
				single['pub_index'] if 'pub_index' in single else single['delay_index']+single['delay_reason'], 
				font=ttf, fill=(0,160,216))
		out = BytesIO()
		final_back.save(out, format='JPEG')
	await app.sendGroupMessage(group, MessageChain.create([
		Image.fromUnsafeBytes(out.getvalue())]))