from graia.ariadne.app import Ariadne
from graia.ariadne.model import Group, Member, MemberPerm
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import *
from graia.ariadne.message.parser.twilight import Twilight, FullMatch, WildcardMatch, SpacePolicy
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

import asyncio
from io import StringIO, BytesIO

from PIL import Image as IMG
from PIL import ImageDraw, ImageFont
from graiax.msgparse import MessageChainParser, MsgString, ParserExit
from prettytable import PrettyTable
from prettytable import FRAME
import regex

from orm import *
from decorators import admin_check
from expand.text import EmojiWriter

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
    listening_events=[GroupMessage], decorators=[admin_check()],
    inline_dispatchers=[Twilight(
        [FullMatch("设置查看")],
        {"custom_group": WildcardMatch(optional=True)}
    )]
))
async def setting_watch(app: Ariadne, group: Group, member: Member, custom_group: WildcardMatch):
    x = PrettyTable()
    x.hrules = FRAME
    x.vrules = FRAME
    x.field_names = ["Plugin name", "switch"]
    x.align["Plugin name"] = "l"
    x.sortby = "Plugin name"
    try:
        g = group.id if not custom_group.matched else int(custom_group.result.asDisplay().strip())
    except ValueError:
        await app.sendGroupMessage(group, MessageChain.create(
            Plain("参数错误，请检查你所填写的参数")
        ))
        return

    def status(b):
        if not b.module.switch:
            return "➖"
        elif b.switch:
            return "✅"
        else:
            return "❌"

    x.add_rows([[f"{b.module.folder}.{b.module.name}", status(b)]
                for b in session.query(ModuleSetting).filter_by(group_id=g).all()])

    def makepic():
        pic = EmojiWriter(font="src/font/SourceHanSansHW-Regular.otf").text2pic(str(x),"white", size=109)
        i = IMG.new("RGB", pic.size)
        i.paste(pic,(0,0),pic)
        i.save(b := BytesIO(), format="JPEG")
        return b.getvalue()

    await app.sendGroupMessage(group, MessageChain.create([
        Image(data_bytes=await asyncio.to_thread(makepic))
    ]))

@channel.use(ListenerSchema(
    listening_events=[GroupMessage], priority=4,
    inline_dispatchers=[Twilight(
        [FullMatch("setting")], {"command": WildcardMatch(optional=True)}
    )]
))
async def setting(app: Ariadne, group: Group, member:Member, command: WildcardMatch):
    ss = session.query(QQGroup).filter(QQGroup.id == group.id).first()

    if not ((ss is None and member.id in saya.access('all_setting')['ultra_administration']) or
            (ss.Permission == 'ultra_administration'
             and member.id in saya.access('all_setting')['ultra_administration']) or
            (ss.Permission == "owner" and member.permission == MemberPerm.Owner) or
            (ss.Permission == "administrator" and member.permission == MemberPerm.Administrator)):
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
    plugin_setting.add_argument('-g', '--group', type=int, nargs='*', help='需要操作的群，不填则为发送消息所在群')
    plugin_setting.add_argument('module', help='需要操作的模块')
    on_or_off = plugin_setting.add_mutually_exclusive_group(required=True)
    on_or_off.add_argument('-on', action='store_true', help='启动该模组')
    on_or_off.add_argument('-off', action='store_true', help='关闭该模组')
    plugin_setting.set_defaults(command_type='plugin')

    try:
        args = parser.parse_args(command.result.asDisplay() if command.matched else "")
    except ParserExit as e:
        ttf = ImageFont.truetype('src/font/SourceHanSans-Medium.otf', 60)
        word = std_output.getvalue()
        back = IMG.new("RGB", ttf.getsize_multiline(word), (0,0,0))
        draw = ImageDraw.Draw(back)
        draw.multiline_text((0,0), word, font=ttf)
        back.save(b := BytesIO(), format='JPEG')
        await app.sendGroupMessage(group, MessageChain.create([
            At(member.id), Plain(' ERROR:' if e.status else ' Help:'),
            Image(data_bytes=b.getvalue())
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
            ms = session.query(ModuleSetting).filter(ModuleSetting.group_id == QQGroup.id).filter(
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
                    gs += [a for a in ab_list if a not in gs.black_list]
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
                        if a not in gs.black_list:
                            gs.black_list.remove(a)
                    session.commit()
                    msg.append(f'已删除{len(ab_list)}人出黑名单')
                else:
                    msg.append(f'Error：该群没有添加设置')

        if args.permission:
            msg.append("Error：管理权限还没写完，下次一定")

    elif args.command_type == 'plugin':

        if args.group is None:
            s = args.module.split('.')
            q1 = session.query(Module).filter(Module.folder == args.module)
            q2 = session.query(Module).filter(Module.folder == '.'.join(s[:-1]),
                                              Module.name == s[-1])

            if session.query(q1.exists()).scalar():
                msg.append(f"已将'{args.module}'内的所有插件{'启用' if args.on else '禁用'}")
                for a in q1.all():
                    a.switch = True if args.on else False
                session.commit()
            elif session.query(q2.exists()).scalar():
                for a in q2.all():
                    a.switch = True if args.on else False
                session.commit()
                msg.append(f"已将插件'{args.module}'{'启用' if args.on else '禁用'}")
            else:
                msg.append(f"Error：找不到您所说的插件")



        else:
            groups = args.group if args.group is not None else [group.id]
            s = args.module.split('.')
            # groups = [s[0] for s in session.query(QQGroup).with_entities(QQGroup.id).all()] # 全群
            q1 = session.query(ModuleSetting).filter(ModuleSetting.module_id == Module.id).filter(
                Module.folder == args.module, ModuleSetting.group_id.in_(groups))
            q2 = session.query(ModuleSetting).filter(ModuleSetting.module_id == Module.id).filter(
                Module.folder == '.'.join(s[:-1]), Module.name == s[-1],
                ModuleSetting.group_id.in_(groups))

            if session.query(q1.exists()).scalar():
                for a in q1.all():
                    a.switch = True if args.on else False
                session.commit()
                msg.append(f"已将群中'{args.module}'内的所有插件{'启用' if args.on else '禁用'}")
            elif session.query(q2.exists()).scalar():
                for a in q2.all():
                    a.switch = True if args.on else False
                session.commit()
                msg.append(f"已将插件'{args.module}'{'启用' if args.on else '禁用'}")
            else:
                msg.append(f"Error：找不到您所说的插件,或者该群没有添加设置")

    if msg:
        await app.sendGroupMessage(group, MessageChain.create([Plain('\n'.join(msg))]))