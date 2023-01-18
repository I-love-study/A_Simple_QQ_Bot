from graia.ariadne.app import Ariadne
from graia.ariadne.model import Group, Member, MemberPerm
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Image
from graia.ariadne.message.parser.twilight import Twilight, FullMatch, WildcardMatch, MatchResult
from graia.saya import Saya, Channel
from graiax.shortcut.saya import listen, decorate, dispatch, priority
from graia.broadcast.builtin.decorators import Depend
from arclet.alconna import Alconna, Args, CommandMeta, Option, Subcommand, Arparma, MultiVar
from arclet.alconna.graia import AlconnaDispatcher, match_path
from graia.broadcast.exceptions import ExecutionStop

import skia
from orm import *
from decorators import admin_check
from utils.text import text2pic

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

@listen(GroupMessage)
@decorate(admin_check())
@dispatch(Twilight(FullMatch("设置查看"), WildcardMatch() @ "custom_group"))
async def setting_watch(app: Ariadne, group: Group, member: Member, custom_group: MatchResult):
    try:
        g = group.id if not custom_group.result else int(custom_group.result.display.strip())
    except ValueError:
        await app.send_group_message(group, MessageChain("参数错误，请检查你所填写的参数"))
        return

    status = lambda b: "➖" if not b.module.switch else "✅" if b.switch else "❌"
    tag = [[f"{b.module.folder}.{b.module.name}", status(b)]
           for b in session.query(ModuleSetting).filter_by(group_id=g).all()]
    gap = 15

    lfont = skia.Font(skia.Typeface.MakeFromFile("static/font/SourceHanSans-Medium.otf"), 20)
    rfont = skia.Font(skia.Typeface.MakeFromFile("static/font/NotoColorEmoji.ttf"), 20)

    group_class = await app.get_group(g)
    assert group_class
    group_text = f"群：{group_class.name}({g})"

    llength = int(max(*[lfont.measureText(t[0]) for t in tag], lfont.measureText(group_text)))
    length = llength + 60
    height = len(tag) * (30 + gap) + 40

    builder = skia.TextBlobBuilder()
    for i, (name, s) in enumerate(tag):
        builder.allocRun(name, lfont, 10, 70+i*(30+gap))
        builder.allocRun(s, rfont, 20+llength, 70+i*(30+gap))

    surface = skia.Surface(length, height)
    canvas = surface.getCanvas()
    canvas.clear(skia.ColorBLACK)
    paint = skia.Paint(AntiAlias=True, Color=skia.ColorWHITE)
    canvas.drawString(group_text, 10, 30, lfont, paint)
    canvas.drawTextBlob(builder.make(), 0, 0, paint)

    paint.setStrokeWidth(3)
    paint.setPathEffect(
        skia.DashPathEffect.Make([15.0, 5.0, 2.0, 5.0], 0.0),
    )
    for i in range(len(tag)):
        canvas.drawLine((0, 80+i*(30+gap)), (length, 80+i*(30+gap)), paint)

    image = surface.makeImageSnapshot()
    b = image.encodeToData(skia.kJPEG, 90).bytes()

    await app.send_message(group, MessageChain(Image(data_bytes=b)))

setting_parse = Alconna(
    "setting",
    Subcommand("group", [
        Option("-ab|--add-black", Args["member;S", int]),
        Option("-db|--del-black", Args["member;S", int]),
        Option("-p|--permission", Args["permission", ['none', 'administrator', 'owner']]),
        Option("-a|--add", action=lambda _: True),
        Option("-d|--delete", action=lambda _: True),
    ], Args["group", MultiVar(int, "*")]),
    Subcommand("module", [
        Option("-g|--group", Args["groups", MultiVar(int, "*")]),
        Option("-on"),
        Option("-off")
    ], Args["module_name", str]))

async def setting_deco(group: Group, member: Member):
    ss = session.query(QQGroup).filter(QQGroup.id == group.id).first()
    assert ss

    if not ((ss is None and member.id in saya.access('all_setting')['ultra_administration']) or
            (ss.Permission == 'ultra_administration'
             and member.id in saya.access('all_setting')['ultra_administration']) or
            (ss.Permission == "owner" and member.permission == MemberPerm.Owner) or
            (ss.Permission == "administrator" and member.permission == MemberPerm.Administrator)):
        raise ExecutionStop

deco = Depend(setting_deco)

@listen(GroupMessage)
@priority(4)
@decorate(deco)
@dispatch(AlconnaDispatcher(setting_parse, send_flag="reply"))
@decorate(match_path("module"))
async def setting_module(app: Ariadne, group: Group, member: Member, result: Arparma):
    on = result.find("module.on")
    off = result.find("module.off")
    lgroup = result.all_matched_args.get("groups", None)
    if lgroup is not None and not lgroup:
        lgroup = (group.id, )

    if not (on ^ off):
        await app.send_message(group, MessageChain("你到底是开还是关啊kora"))
        return

    msg = ""

    module_name = result["module_name"]
    s = result["module_name"].split(".")
    parent = ".".join(s[:-1])
    module_names = s[-1].split("|") if "|" in result["module_name"] else [s[-1]]
    q1_module = [Module.folder.in_([f"{parent}.{m}" for m in module_names])]
    q2_module = [Module.folder == parent, Module.name.in_(module_names)]

    if lgroup is None:
        q1 = session.query(Module).filter(q1_module)
        q2 = session.query(Module).filter(q2_module)
    else:
        q1 = session.query(ModuleSetting).filter(ModuleSetting.module_id == Module.id).filter(
            *q1_module, ModuleSetting.group_id.in_(lgroup))
        q2 = session.query(ModuleSetting).filter(ModuleSetting.module_id == Module.id).filter(
            *q2_module, ModuleSetting.group_id.in_(lgroup))

        if session.query(q1.exists()).scalar():
            msg += f"已将{'群中' if lgroup else ''}'{s}'内的所有插件{'启用' if on else '禁用'}"
            for a in q1.all():
                a.switch = on
            session.commit()
        elif session.query(q2.exists()).scalar():
            for a in q2.all():
                a.switch = on
            session.commit()
            msg += f"已将{'群中' if lgroup else ''}插件'{module_name}'{'启用' if on else '禁用'}"
        else:
            msg += f"Error：找不到您所说的插件{',或者该群没有添加设置' if lgroup else ''}"
    
    await app.send_message(group, MessageChain(msg))

@listen(GroupMessage)
@priority(4)
@decorate(deco)
@dispatch(AlconnaDispatcher(setting_parse, send_flag="reply"))
@decorate(match_path("group"))
async def setting_group(app: Ariadne, group: Group, member:Member, result: Arparma):
    msg = []
    lgroup = result.all_matched_args.get("group", None)
    if not lgroup:
        lgroup = [group.id]

    if result.find("add"):
        success, repeat = [], []
        for g in lgroup:
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

    if result.find("delete"):
        ms = session.query(ModuleSetting).filter(ModuleSetting.group_id == QQGroup.id).filter(
            QQGroup.id.in_(lgroup)).all()
        [session.delete(u) for u in ms]
        g = session.query(QQGroup).filter(QQGroup.id.in_(lgroup)).all()
        [session.delete(u) for u in g]
        session.commit()
        msg.append('已删除群组设置:' + '、'.join(str(g) for g in lgroup))

    if result.find("add_black"):
        ab_list = result["member"]
        if len(lgroup) > 1:
            msg.append('Error：黑名单单次只允许设置一个组的')
        else:
            gs = session.query(QQGroup).filter_by(id=lgroup[0]).first()
            if gs:
                gs += [a for a in ab_list if a not in gs.black_list]
                session.commit()
                msg.append(f'已添加{len(ab_list)}人进黑名单')
            else:
                msg.append(f'Error：该群没有添加设置')

    if result.find("del_black"):
        ab_list = result["member"]
        if len(lgroup) > 1:
            msg.append('Error：黑名单单次只允许设置一个组的')
        else:
            gs = session.query(QQGroup).filter_by(id=lgroup[0]).first()
            if gs:
                for a in ab_list:
                    if a not in gs.black_list:
                        gs.black_list.remove(a)
                session.commit()
                msg.append(f'已删除{len(ab_list)}人出黑名单')
            else:
                msg.append(f'Error：该群没有添加设置')

    if result.find("permission"):
        msg.append("Error：管理权限还没写完，下次一定")

    if msg:
        await app.send_group_message(group, MessageChain('n'.join(msg)))