from graia.application import GraiaMiraiApplication
from graia.application.event.messages import GroupMessage
from graia.application.message.elements.internal import Plain, Image
from graia.application.message.chain import MessageChain
from graia.application.message.parser.kanata import Kanata
from graia.application.message.parser.signature import FullMatch, RequireParam
from graia.application.group import Group, Member

from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

import aiohttp
from urllib.parse import quote

channel = Channel.current()

channel.name("BangumiData")
channel.description("发送'bangumi [番剧]'获取番剧详细信息")
channel.author("I_love_study")


@channel.use(ListenerSchema(
	listening_events=[GroupMessage],
	inline_dispatchers=[Kanata([FullMatch('bangumi'), RequireParam('tag')])]
	))
async def anime(app: GraiaMiraiApplication, group: Group, message: MessageChain, member: Member, tag: MessageChain):
	bangumi_headers = {
	"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "\
				  "AppleWebKit/537.36 (KHTML, like Gecko) "\
				  "Chrome/84.0.4147.135 Safari/537.36"}
	url = 'https://api.bgm.tv/search/subject/{}?type=2&responseGroup=Large&max_results=1'.format(
		quote(tag.asDisplay().strip()))
	async with aiohttp.request("GET", url, headers = bangumi_headers) as r:
		data = await r.json()

	if "code" in data.keys() and data["code"] == 404:
		await app.sendGroupMessage(group, MessageChain.create([
			Plain('sorry,搜索不到相关信息')]))
		return

	detail_url = f'https://api.bgm.tv/subject/{data["list"][0]["id"]}?responseGroup=medium'
	async with aiohttp.request("GET", detail_url) as r:
		data = await r.json()
	await app.sendGroupMessage(group, MessageChain.create([
		Image.fromNetworkAddress(data["images"]["large"]),
		Plain(text=f"名字:{data['name_cn']}({data['name']})\n"),
		Plain(text=f"简介:{data['summary']}\n"),
		Plain(text=f"bangumi评分:{data['rating']['score']}(参与评分{data['rating']['total']}人)\n"),
		Plain(text=f"bangumi排名:{data['rank']}" if 'rank' in data else '')
		]))