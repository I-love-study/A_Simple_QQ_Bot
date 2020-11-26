from graia.application import GraiaMiraiApplication
from graia.application.event.messages import GroupMessage
from graia.application.message.elements.internal import Plain, At
from graia.application.message.chain import MessageChain
from graia.application.group import Group, Member
#from graia.application.exceptions import 
from core import judge
from core import get

import random

__plugin_name__ = '禁言我'
__plugin_usage__ = '说"禁言我"'

bcc = get.bcc()
@bcc.receiver(GroupMessage, headless_decoraters = [judge.group_check(__name__)])#禁言
async def auto_ban(app: GraiaMiraiApplication, group: Group, message: MessageChain, member:Member):
    msg_str = message.asDisplay().strip()
    if '禁言我' in msg_str and len(msg_str) <= 4 :
        try:
            await app.mute(group, member, 600)
            await app.sendGroupMessage(group, MessageChain.create([
                Plain('那我就来实现你的愿望吧！')]))
        except PermissionError:
            await app.sendGroupMessage(group, MessageChain.create([
                Plain('对不起，我没有办法实现你的愿望555~')]))