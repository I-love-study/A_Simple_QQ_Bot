from graia.application import GraiaMiraiApplication
from graia.application.event.messages import GroupMessage
from graia.application.message.parser.kanata import Kanata
from graia.application.message.parser.signature import RegexMatch
from graia.application.message.elements.internal import Plain, At
from graia.application.message.chain import MessageChain
from graia.application.group import Group, Member
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

channel = Channel.current()

channel.name("BanMe")
channel.description("发送'禁言我'禁言(前提是有权限)")
channel.author("I_love_study")

@channel.use(ListenerSchema(
    listening_events=[GroupMessage],
    inline_dispatchers=[Kanata([RegexMatch('.禁言我.')])]
    ))
async def auto_ban(app: GraiaMiraiApplication, group: Group, message: MessageChain, member:Member):
    try:
        await app.mute(group, member, 600)
        await app.sendGroupMessage(group, MessageChain.create([
            Plain('那我就来实现你的愿望吧！')]))
    except PermissionError:
        await app.sendGroupMessage(group, MessageChain.create([
            Plain('对不起，我没有办法实现你的愿望555~')]))