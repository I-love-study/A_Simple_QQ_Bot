from graia.application import GraiaMiraiApplication
from graia.application.event.messages import GroupMessage
from graia.application.message.elements.internal import Plain, At
from graia.application.message.chain import MessageChain
from graia.application.group import Group, Member
from core import judge
from core import get

__plugin_name__ = '禁言我'
__plugin_usage__ = '说"禁言我"'

bcc = get.bcc()
@bcc.receiver(GroupMessage, headless_decoraters = [judge.group_check(__name__)])#禁言
async def auto_ban(app: GraiaMiraiApplication, group: Group, message: MessageChain, member:Member):
    if message.asDisplay().strip() in ['禁言我','我要禁言']:
        await app.mute(group, member, 600)
        await app.sendGroupMessage(member.group, MessageChain.create([Plain('好，那我就成全你')]))
        await app.sendGroupMessage(member.group, MessageChain.create([Plain('时精屋雅座一位')]))