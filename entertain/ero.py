from graia.application import GraiaMiraiApplication
from graia.application.event.messages import GroupMessage
from graia.application.message.elements.internal import *
from graia.application.message.chain import MessageChain
from graia.application.message.parser.kanata import Kanata
from graia.application.message.parser.signature import FullMatch, OptionalParam
from graia.application.group import Group, Member, MemberPerm
from graia.broadcast.exceptions import ExecutionStop
from graiax.msgparse import MessageChainParser, MsgString, ParserExit
from core import get
from core import judge
from expand.save import Group_save

from PIL import Image as IMG
from PIL import ImageDraw, ImageFont
from datetime import datetime, date
from pathlib import Path
from io import StringIO, BytesIO

import aiohttp
import random
import time

power = {
	'none': [],
	'owner': [MemberPerm.Owner],
	'administrator': [MemberPerm.Owner, MemberPerm.Administrator]}

ero_setting = Group_save.get('data/ero_setting.json')
lsps = Group_save.get('data/lsps.json')
ultra_admin = []
apikey = ''


def ero_check(group: Group):
	if ero_setting.get_item(group.id).get('status') is not True:
		raise ExecutionStop()

bcc = get.bcc()
@bcc.receiver(
	GroupMessage,
	headless_decorators = [judge.config_check(__name__)],
	dispatchers=[Kanata([FullMatch('涩图来'), OptionalParam('tag')])]
	)
async def ero_pic(app: GraiaMiraiApplication, group: Group, member: Member, tag):
	global ero_f, apikey
	g_setting = ero_setting.get_item(group.id)
	getup = datetime.fromisoformat(date.today().isoformat()+"T06:30")
	sleep = datetime.fromisoformat(date.today().isoformat()+"T23:00")
	lsp = lsps.get_item(group.id, member.id, date.today())
	if not g_setting.get('status'):
		msg = '我们这个群是正经群，不搞这些玩意的'
	elif member.id in g_setting.get('black_list', []):
		msg = '黑名单人是没有涩图看的'
	elif not getup < datetime.now() < sleep and not g_setting.get('compel'):
		msg = '我要睡觉,不要打扰我'
	elif lsp.get('t', [0])[-1] >= time.time()-g_setting.get('group_frame', 0):
		msg = '你太快了,少*点'

	else:
		ero_from = g_setting.get('source', 'web')
		
		lsp.setdefault('num', 0)
		lsp.setdefault('t', [])
		lsp['num'] += 1
		lsp['t'].append(time.time())
		if ero_from == 'web':
			parmas = {
				'apikey' : apikey,
				'r18' : 0,
				'proxy' : 'disable',
				'size1200' : 'true'}
			if tag:
				parmas['keyword'] = tag.asDisplay()
			async with aiohttp.request("GET", url='https://api.lolicon.app/setu/', params=parmas) as r:
				pic_info = await r.json()
			if pic_info['code'] == 429:
				msg = '玛德你们这群lsp调用次数全™用完了'
			elif not pic_info['data']:
				msg = MessageChain.create([
					At(target = member.id),
					Plain(text = '没搜索到相关色图'),
					Plain(text = f"\n剩余调用次数:{pic_info['quota']}")])
			else:
				headers = {
					'Referer': 'https://www.pixiv.net/member_illust.php?mode=medium&illust_id',
					'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '\
								  '(KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
				single_pic = pic_info['data'][0]
				async with aiohttp.request("GET", single_pic['url'], headers=headers) as r:
					setu = await r.read()
				msg = MessageChain.create([
					At(target = member.id),
					Plain(text = '\n您要的涩图'),
					Plain(text = f"\npid:{single_pic['pid']}"),
					Plain(text = f"\n{single_pic['title']}/{single_pic['author']}"),
					Plain(text = f"\n剩余调用次数:{pic_info['quota']}"),
					Image.fromUnsafeBytes(setu)])
		elif ero_from == 'local':
			ero_pics = [Path('data/ero_pic').iterdir()]
			msg = MessageChain.create([Image.fromLocalFile(random.choice(ero_pics))])

	if msg is not None:
		await app.sendGroupMessage(group,
			msg if type(msg) is MessageChain else MessageChain.create([Plain(msg)]))

@bcc.receiver(
	GroupMessage,
	headless_decorators = [judge.config_check(__name__)],
	dispatchers=[Kanata([FullMatch('lsp排行榜')])]
	)
async def lsps_rank():
	spdata = lsps.get_item(group.id)
	today_sp = sorted(spdata.items(), key=lambda x: x['num'], reverse=True)
	msg = [Plain('lsp排行榜')]
	for lsp, n in today_sp.items():
		lsp_info = await app.getMember(group, int(lsp))
		msg.append(Plain(f"\n{lsp_info.name}\n调用{n['num']}次"))
	await app.sendGroupMessage(group, MessageChain.create(send))

@bcc.receiver(
	GroupMessage,
	dispatchers=[Kanata([FullMatch('setu'), OptionalParam('tag')])]
	)
async def setting_ero(app: GraiaMiraiApplication, group: Group, member: Member, tag):
	g_setting = ero_setting.get_item(group.id)
	if member.id not in ultra_admin:
		if member.permission not in power[g_setting.get('power', 'none')]:
			return

	std_output = StringIO()
	parser = MessageChainParser(prog='setu_setting', std=std_output, )
	subparser = parser.add_subparsers(metavar='command', )

	group_setting = subparser.add_parser('group', std=std_output)
	group_setting.add_argument('-g', '--group', type=int, default=group.id,
		help='需要执行的组(没有则自动选择所在组)')
	group_setting.add_argument('-p', '--power', action='store', choices={'none', 'administrator', 'owner'},
		help='可操控权限')
	group_setting.add_argument('-s', '--source', action='store', choices={'web','local'},
		help='选择涩图来源')

	status = group_setting.add_mutually_exclusive_group()
	status.add_argument('-on', action='store_true', help='在群启动涩图功能')
	status.add_argument('-off', action='store_true', help='在群关闭涩图功能')

	compel = group_setting.add_mutually_exclusive_group()
	compel.add_argument('-c', '--compel', action='store_true', help='启动加班模式')
	compel.add_argument('-r', '--rest', action='store_true', help='关闭加班模式')

	group_setting.set_defaults(command_type='group')

	member_setting = subparser.add_parser('member', std=std_output)
	member_setting.add_argument('-m', '--member', type=MsgString.decode())
	member_setting.add_argument('-ab', '--add_black', type=MsgString.decode(), help='添加黑名单')
	member_setting.add_argument('-db', '--delate_black', type=MsgString.decode(), help='删除黑名单')
	member_setting.add_argument('-mt', '--member_frame', type=int, help='单人调用涩图间隔(单位s)')
	member_setting.set_defaults(command_type='member')

	try:
		args = parser.parse_args('' if tag is None else tag.asDisplay())
	except ParserExit as e:
		ttf = ImageFont.truetype('src/font/SourceHanSans-Medium.otf', 60)
		word = std_output.getvalue()
		back = IMG.new("RGB", ttf.getsize_multiline(word), (0,0,0))
		draw = ImageDraw.Draw(back)
		draw.multiline_text((0,0), word, font=ttf)
		b = BytesIO()
		back.save(b, format='JPEG')
		await app.sendGroupMessage(group, MessageChain.create([
			At(member.id), Plain(' ERROR:' if e.status else ' Help:'),
			Image.fromUnsafeBytes(b.getvalue())
			]))
		return

	if args.command_type == 'group':
		if member.id not in ultra_admin and args.group != group.id:
			await app.sendGroupMessage(group, MessageChain.create([
				Plain('你并没有修改其他群的权限')]))
			return

		setting_group = ero_setting.get_item(args.group)
		msg = []
		if args.on:
			setting_group['status']=True
			msg.append('涩图模式已启动')
		elif args.off:
			setting_group['status']=False
			msg.append('涩图模式已关闭')
		if args.compel:
			setting_group['compel']=True
			msg.append('加班模式已启动')
		elif args.rest:
			setting_group['compel']=False
			msg.append('加班模式已关闭')
		if args.source:
			setting_group['source']=args.source
			msg.append(f'涩图来源以更换为:{args.source}')
		if args.power:
			setting_group['power']=args.power
			msg.append(f'涩图设置权限已更换为:{args.power}')

		if msg:
			await app.sendGroupMessage(group, MessageChain.create([
				Plain('\n'.join(msg))]))
			ero_setting.commit()

	if args.command_type == 'member':
		if member.id not in ultra_admin:
			await app.sendGroupMessage(group, MessageChain.create([
				Plain('你并没有这项权限')]))

		msg=[]
		g_setting.setdefault('black_list', [])
		if args.add_black:
			if ab.has(At):
				ab_list = [a.target for a in ab.get(At)]
			else: 
				li = regex.split('[ ,，]', ab.asDisplay().strip())
				ab_list = [int(li) for a in li if li.isdigit()]
			ab_list = [a for a in ab_list if a not in g_setting['black_list']]
			g_setting['black_list'].extend(ab_list)
			msg.append(f'已添加{len(ab_list)}人进黑名单')
		if args.delate_black:
			if ab.has(At):
				ab_list = [a.target for a in ab.get(At)]
			else: 
				li = regex.split('[ ,，]', ab.asDisplay().strip())
				ab_list = [int(li) for a in li if li.isdigit()]
			ab_list = [a for a in ab_list if a in g_setting['black_list']]
			for a in ab_list:
				g_setting['black_list'].remove(a)
			msg.append(f'已删除{len(ab_list)}人出黑名单')
		if args.member_frame is not None:
			setting_group['member_frame']=args.member_frame
			msg.append(f'单人涩图频率已更换为:{args.member_frame}s')

		if msg:
			await app.sendGroupMessage(group, MessageChain.create([
				Plain('\n'.join(msg))]))