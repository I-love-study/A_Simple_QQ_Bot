from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.parser.base import MatchRegex
from graia.ariadne.model import Group, Member
from graia.saya import Channel
from graiax.shortcut.saya import listen, decorate

channel = Channel.current()

channel.name("BanMe")
channel.description("发送'禁言我'禁言(前提是有权限)")
channel.author("I_love_study")

@listen(GroupMessage)
@decorate(MatchRegex(".?禁言我.?"))
async def auto_ban(app: Ariadne, group: Group, member: Member):
    try:
        await app.mute_member(group, member, 600)
        await app.send_group_message(group, MessageChain('那我就来实现你的愿望吧！'))
    except PermissionError:
        await app.send_group_message(group, MessageChain('对不起，我没有办法实现你的愿望555~'))