from graia.broadcast.builtin.decoraters import Depend
from graia.application import GraiaMiraiApplication
from graia.application.event.mirai import MemberJoinEvent, MemberLeaveEventKick, MemberLeaveEventQuit
from graia.application.message.elements.internal import Plain, Image, At
from graia.application.message.chain import MessageChain
from graia.application.group import Group, Member

from expand import judge
from core import get
import asyncio

bcc = get.bcc()

@bcc.receiver(MemberJoinEvent, headless_decoraters = [Depend(judge.active_check_in)])#入群
async def welcome(app: GraiaMiraiApplication, member: Member):
    await app.sendGroupMessage(member.group, MessageChain.create([
        Image.fromLocalFile(r'join.jpg'),
        At(target = member.id),
        Plain(text = '欢迎大佬来到PLUS ULTRA!'),
        Plain(text = '\n记得改备注哦')
        ]))