from graia.broadcast.builtin.decoraters import Depend
from graia.application import GraiaMiraiApplication
from graia.application.event.messages import GroupMessage
from graia.application.message.elements.internal import Plain, At, App
from graia.application.message.chain import MessageChain
from graia.application.group import Group, Member
from graia.scheduler import timers

from expand import Netease
from core import get

app = get.app()
sche = get.sche()

@sche.schedule(timers.crontabify('0 23 * * *'))
async def sleep():
    await app.sendGroupMessage(1009529133, MessageChain.create([Plain('现在是北京时间23点\n祝各位晚安，好梦')]))

@sche.schedule(timers.crontabify('30 6 * * *'))
async def get_up():
    await app.sendGroupMessage(1009529133, MessageChain.create([Plain('现在是北京时间6点30分\n大家早上好')]))
    card = await Netease.app_card(393685)
    await app.sendGroupMessage(1009529133, MessageChain.create([App(content = card)]))

@sche.schedule(timers.crontabify('30 17 * * 3'))
async def after_school():
    await app.sendGroupMessage(1009529133, MessageChain.create([Plain('该社团活动了')]))
    card = await Netease.app_card(479219061)
    await app.sendGroupMessage(1009529133, MessageChain.create([App(content = card)]))