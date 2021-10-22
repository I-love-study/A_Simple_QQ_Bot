from graia.application import GraiaMiraiApplication
from graia.application.event.messages import GroupMessage
from graia.application.message.elements.internal import *
from graia.application.message.chain import MessageChain
from graia.application.group import Group, Member
from graia.application.message.parser.kanata import Kanata
from graia.application.message.parser.signature import FullMatch, OptionalParam
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

from PIL import Image as IMG
from PIL import ImageDraw, ImageFont
import regex
from graiax.msgparse import MessageChainParser, MsgString, ParserExit
from io import StringIO, BytesIO

from orm import *

class GetSetting:

	def __init__(self):
		pass

	def get_active_group(self, name):
		sp = name.split('.')
		folders = [q.folder.split('.') for q in session.query(Module).all()]
		folder = next(f for f in folders if sp[:len(f)] == f)
		ss = session.query(Module).filter_by(
			folder = '.'.join(folder), 
			name   = sp[len(folder)]).first()
		return [s.group_id for s in ss.setting if s.switch] if ss else []

saya = Saya.current()
channel = Channel.current()
@channel.use(ListenerSchema(
    listening_events=[GroupMessage], priority=8,
    inline_dispatchers=[Kanata([FullMatch('setting'), OptionalParam('tag')])]
    ))
async def setting(app: GraiaMiraiApplication, group: Group, member:Member, tag):
	ss = session.query(QQGroup).filter(QQGroup.id == group.id).first()
	if ss == 'ultra_administration' and member.id not in saya.access('all_setting')['ultra_administration']:
		return

	msg = []
	std_output = StringIO()
	parser = MessageChainParser(prog='plugin_setting', std=std_output)
	subparser = parser.add_subparsers(metavar='command')

	#增加/删去群组设置
	group_setting = subparser.add_parser('group', std=std_output)
	group_setting.add_argument('group', type=int, nargs='*', help='要操作的组(可多选)')
	group_setting.add_argument('-ab', '--add_black', type=MsgString.decode(), help='添加黑名单')
	group_setting.add_argument('-db', '--del_black', type=MsgString.decode(), help='删除黑名单')
	group_setting.add_argument('-p', '--permission', choices={'none', 'administrator', 'owner'}, 
		help='可操控权限(还没写完)')
	add_or_del = group_setting.add_mutually_exclusive_group()
	add_or_del.add_argument('-a', '--add'   , action='store_true', help='加入数据库')
	add_or_del.add_argument('-d', '--delete', action='store_true', help='移出数据库')
	group_setting.set_defaults(command_type='group')

	#群内各插件设置
	plugin_setting = subparser.add_parser('plugin', std=std_output)
	plugin_setting.add_argument('-g', '--group', type=int, nargs='*', help='需要操作的群')
	plugin_setting.add_argument('module', help='需要操作的模块')
	on_or_off = plugin_setting.add_mutually_exclusive_group(required=True)
	on_or_off.add_argument('-on', action='store_true', help='启动该模组')
	on_or_off.add_argument('-off', action='store_true', help='关闭该模组')
	plugin_setting.set_defaults(command_type='plugin')

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
		groups = args.group if args.group else [group.id]
		if args.add:
			success, repeat = [], []
			for g in groups:
				if not session.query(QQGroup).filter_by(id=g).first():
					ms = [ModuleSetting(module_id=m.id, switch=True) for m in session.query(Module).all()]
					session.add_all(ms)
					session.add(QQGroup(id=g, setting=ms))
					success.append(g)
				else:
					repeat.append(g)
			session.commit()
			if success:
				msg.append('已增加群组设置:' + '、'.join(str(g) for g in success))
			if repeat:
				msg.append('有群组设置早已增加:' + '、'.join(str(g) for g in repeat))
		if args.delete:
			ms = session.query(ModuleSetting).filter(ModuleSetting.group_id==QQGroup.id).filter(
				QQGroup.id.in_(groups)).all()
			[session.delete(u) for u in ms]
			g = session.query(QQGroup).filter(QQGroup.id.in_(groups)).all()
			[session.delete(u) for u in g]
			session.commit()
			msg.append('已删除群组设置:' + '、'.join(str(g) for g in groups))
		if args.add_black:
			if args.add_black.has(At):
				ab_list = [a.target for a in args.add_black.get(At)]
			else: 
				li = regex.split('[ ,，]', args.add_black.asDisplay().strip())
				ab_list = [int(li) for a in li if li.isdigit()]
			if len(groups) > 1:
				msg.append('Error：黑名单单次只允许设置一个组的')
			else:
				gs = session.query(QQGroup).filter_by(id=g).first()
				if gs:
					for a in ab_list:
						if a not in gs.black_list: gs.black_list.append(a)
					session.commit()
					msg.append(f'已添加{len(ab_list)}人进黑名单')
				else:
					msg.append(f'Error：该群没有添加设置')
		if args.del_black:
			if args.add_black.has(At):
				ab_list = [a.target for a in args.add_black.get(At)]
			else: 
				li = regex.split('[ ,，]', args.add_black.asDisplay().strip())
				ab_list = [int(li) for a in li if li.isdigit()]
			if len(groups) > 1:
				msg.append('Error：黑名单单次只允许设置一个组的')
			else:
				gs = session.query(QQGroup).filter_by(id=g).first()
				if gs:
					for a in ab_list:
						if a not in gs.black_list: gs.black_list.remove(a)
					session.commit()
					msg.append(f'已删除{len(ab_list)}人出黑名单')
				else:
					msg.append(f'Error：该群没有添加设置')
		if args.permission:
			msg.append("Error：管理权限还没写完，下次一定")
	elif args.command_type == 'plugin':
		groups = args.group if args.group is not None else [group.id]
		q = session.query(ModuleSetting).filter(
			ModuleSetting.module_id == Module.id).filter(
			Module.folder == args.module,
			ModuleSetting.group_id.in_(groups)
			)
		if session.query(q.exists()).scalar(): 
			for a in q.all(): a.switch = True if args.on else False
			session.commit()
			msg.append(f"已将'{args.module}'内的所有插件{'启用' if args.on else '禁用'}")
		else:
			s = args.module.split('.')
			q = session.query(ModuleSetting).filter(
				ModuleSetting.module_id == Module.id).filter(
				Module.folder == '.'.join(s[:-1]), 
				Module.name == s[-1],
				ModuleSetting.group_id.in_(groups))
			if session.query(q.exists()).scalar():
				for a in q.all(): a.switch = True if args.on else False
				session.commit()
				msg.append(f"已将插件'{args.module}'{'启用' if args.on else '禁用'}")
			else:
				msg.append(f"Error：找不到您所说的插件,或者该群没有添加设置")

	if msg:
		await app.sendGroupMessage(group, MessageChain.create([Plain('\n'.join(msg))]))