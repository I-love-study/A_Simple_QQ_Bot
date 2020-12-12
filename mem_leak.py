import asyncio
from graia.broadcast import Broadcast

from graia.broadcast.builtin.decoraters import Depend
from graia.broadcast.exceptions import ExecutionStop
from graia.application.message.parser.kanata import Kanata
from graia.application.message.parser.signature import RegexMatch

from graia.application.entry import (
    GraiaMiraiApplication, Session,
    MemberJoinEvent, MemberLeaveEventKick, MemberLeaveEventQuit,
    GroupMessage, Group, Member,
    MessageChain, Plain, MemberPerm,
    At, Quote, Source, Image, FlashImage, App)

from graia.scheduler import timers
import graia.scheduler
from graia.application.logger import LoggingLogger

robot_id = 1176706232
active_group = [806724946]

loop = asyncio.get_event_loop()

bcc = Broadcast(loop = loop, debug_flag = True)
app = GraiaMiraiApplication(
    broadcast=bcc,
    connect_info=Session(
        host="http://localhost:8070", # 填入 httpapi 服务运行的地址
        authKey="I_Love_Study", # 填入 authKey
        account=robot_id, # 你的机器人的 qq 号
        websocket=True, # Graia 已经可以根据所配置的消息接收的方式来保证消息接收部分的正常运作.
        debug_flag=True
    )
)
sche = graia.scheduler.GraiaScheduler(loop = loop, broadcast=bcc)
import objgraph
import random

def test(group: Group):
    if group.id not in active_group:
        raise ExecutionStop()

@bcc.receiver(GroupMessage,
    headless_decoraters = [Depend(test)],
    dispatchers = [Kanata([RegexMatch('test.*')])])
async def auto_ban(app: GraiaMiraiApplication, group: Group, message: MessageChain, member:Member):
        print(objgraph.show_growth())

@bcc.receiver(GroupMessage,
    headless_decoraters = [Depend(test)],
    dispatchers = [Kanata([RegexMatch('test.*')])])
async def auto_ban(app: GraiaMiraiApplication, group: Group, message: MessageChain, member:Member):
        await app.sendGroupMessage(group, MessageChain.create([Plain('ohh\n'),Plain(random.randint(1,10))]))

@bcc.receiver(GroupMessage,
    headless_decoraters = [Depend(test)],
    dispatchers = [Kanata([RegexMatch('test.*')])])
async def auto_ban(app: GraiaMiraiApplication, group: Group, message: MessageChain, member:Member):
        ...

@bcc.receiver(GroupMessage,
    headless_decoraters = [Depend(test)],
    dispatchers = [Kanata([RegexMatch('test.*')])])
async def auto_ban(app: GraiaMiraiApplication, group: Group, message: MessageChain, member:Member):
        ...
@bcc.receiver(GroupMessage,
    headless_decoraters = [Depend(test)],
    dispatchers = [Kanata([RegexMatch('test.*')])])
async def auto_ban(app: GraiaMiraiApplication, group: Group, message: MessageChain, member:Member):
        ...
@bcc.receiver(GroupMessage,
    headless_decoraters = [Depend(test)],
    dispatchers = [Kanata([RegexMatch('test.*')])])
async def auto_ban(app: GraiaMiraiApplication, group: Group, message: MessageChain, member:Member):
        ...
@bcc.receiver(GroupMessage,
    headless_decoraters = [Depend(test)],
    dispatchers = [Kanata([RegexMatch('test.*')])])
async def auto_ban(app: GraiaMiraiApplication, group: Group, message: MessageChain, member:Member):
        ...
@bcc.receiver(GroupMessage,
    headless_decoraters = [Depend(test)],
    dispatchers = [Kanata([RegexMatch('test.*')])])
async def auto_ban(app: GraiaMiraiApplication, group: Group, message: MessageChain, member:Member):
        ...
@bcc.receiver(GroupMessage,
    headless_decoraters = [Depend(test)],
    dispatchers = [Kanata([RegexMatch('test.*')])])
async def auto_ban(app: GraiaMiraiApplication, group: Group, message: MessageChain, member:Member):
        ...
@bcc.receiver(GroupMessage,
    headless_decoraters = [Depend(test)],
    dispatchers = [Kanata([RegexMatch('test.*')])])
async def auto_ban(app: GraiaMiraiApplication, group: Group, message: MessageChain, member:Member):
        ...
@bcc.receiver(GroupMessage,
    headless_decoraters = [Depend(test)],
    dispatchers = [Kanata([RegexMatch('test.*')])])
async def auto_ban(app: GraiaMiraiApplication, group: Group, message: MessageChain, member:Member):
        ...
@bcc.receiver(GroupMessage,
    headless_decoraters = [Depend(test)],
    dispatchers = [Kanata([RegexMatch('test.*')])])
async def auto_ban(app: GraiaMiraiApplication, group: Group, message: MessageChain, member:Member):
        ...
@bcc.receiver(GroupMessage,
    headless_decoraters = [Depend(test)],
    dispatchers = [Kanata([RegexMatch('test.*')])])
async def auto_ban(app: GraiaMiraiApplication, group: Group, message: MessageChain, member:Member):
        ...
@bcc.receiver(GroupMessage,
    headless_decoraters = [Depend(test)],
    dispatchers = [Kanata([RegexMatch('test.*')])])
async def auto_ban(app: GraiaMiraiApplication, group: Group, message: MessageChain, member:Member):
        ...
@bcc.receiver(GroupMessage,
    headless_decoraters = [Depend(test)],
    dispatchers = [Kanata([RegexMatch('test.*')])])
async def auto_ban(app: GraiaMiraiApplication, group: Group, message: MessageChain, member:Member):
        ...
@bcc.receiver(GroupMessage,
    headless_decoraters = [Depend(test)],
    dispatchers = [Kanata([RegexMatch('test.*')])])
async def auto_ban(app: GraiaMiraiApplication, group: Group, message: MessageChain, member:Member):
        ...
@bcc.receiver(GroupMessage,
    headless_decoraters = [Depend(test)],
    dispatchers = [Kanata([RegexMatch('test.*')])])
async def auto_ban(app: GraiaMiraiApplication, group: Group, message: MessageChain, member:Member):
        ...
@bcc.receiver(GroupMessage,
    headless_decoraters = [Depend(test)],
    dispatchers = [Kanata([RegexMatch('test.*')])])
async def auto_ban(app: GraiaMiraiApplication, group: Group, message: MessageChain, member:Member):
        ...
@bcc.receiver(GroupMessage,
    headless_decoraters = [Depend(test)],
    dispatchers = [Kanata([RegexMatch('test.*')])])
async def auto_ban(app: GraiaMiraiApplication, group: Group, message: MessageChain, member:Member):
        ...
@bcc.receiver(GroupMessage,
    headless_decoraters = [Depend(test)],
    dispatchers = [Kanata([RegexMatch('test.*')])])
async def auto_ban(app: GraiaMiraiApplication, group: Group, message: MessageChain, member:Member):
        ...
@bcc.receiver(GroupMessage,
    headless_decoraters = [Depend(test)],
    dispatchers = [Kanata([RegexMatch('test.*')])])
async def auto_ban(app: GraiaMiraiApplication, group: Group, message: MessageChain, member:Member):
        ...
@bcc.receiver(GroupMessage,
    headless_decoraters = [Depend(test)],
    dispatchers = [Kanata([RegexMatch('test.*')])])
async def auto_ban(app: GraiaMiraiApplication, group: Group, message: MessageChain, member:Member):
        ...
@bcc.receiver(GroupMessage,
    headless_decoraters = [Depend(test)],
    dispatchers = [Kanata([RegexMatch('test.*')])])
async def auto_ban(app: GraiaMiraiApplication, group: Group, message: MessageChain, member:Member):
        ...
@bcc.receiver(GroupMessage,
    headless_decoraters = [Depend(test)],
    dispatchers = [Kanata([RegexMatch('test.*')])])
async def auto_ban(app: GraiaMiraiApplication, group: Group, message: MessageChain, member:Member):
        ...
@bcc.receiver(GroupMessage,
    headless_decoraters = [Depend(test)],
    dispatchers = [Kanata([RegexMatch('test.*')])])
async def auto_ban(app: GraiaMiraiApplication, group: Group, message: MessageChain, member:Member):
        ...
@bcc.receiver(GroupMessage,
    headless_decoraters = [Depend(test)],
    dispatchers = [Kanata([RegexMatch('test.*')])])
async def auto_ban(app: GraiaMiraiApplication, group: Group, message: MessageChain, member:Member):
        ...
@bcc.receiver(GroupMessage,
    headless_decoraters = [Depend(test)],
    dispatchers = [Kanata([RegexMatch('test.*')])])
async def auto_ban(app: GraiaMiraiApplication, group: Group, message: MessageChain, member:Member):
        ...
@bcc.receiver(GroupMessage,
    headless_decoraters = [Depend(test)],
    dispatchers = [Kanata([RegexMatch('test.*')])])
async def auto_ban(app: GraiaMiraiApplication, group: Group, message: MessageChain, member:Member):
        ...
@bcc.receiver(GroupMessage,
    headless_decoraters = [Depend(test)],
    dispatchers = [Kanata([RegexMatch('test.*')])])
async def auto_ban(app: GraiaMiraiApplication, group: Group, message: MessageChain, member:Member):
        ...
@bcc.receiver(GroupMessage,
    headless_decoraters = [Depend(test)],
    dispatchers = [Kanata([RegexMatch('test.*')])])
async def auto_ban(app: GraiaMiraiApplication, group: Group, message: MessageChain, member:Member):
        ...
@bcc.receiver(GroupMessage,
    headless_decoraters = [Depend(test)],
    dispatchers = [Kanata([RegexMatch('test.*')])])
async def auto_ban(app: GraiaMiraiApplication, group: Group, message: MessageChain, member:Member):
        ...
@bcc.receiver(GroupMessage,
    headless_decoraters = [Depend(test)],
    dispatchers = [Kanata([RegexMatch('test.*')])])
async def auto_ban(app: GraiaMiraiApplication, group: Group, message: MessageChain, member:Member):
        ...
@bcc.receiver(GroupMessage,
    headless_decoraters = [Depend(test)],
    dispatchers = [Kanata([RegexMatch('test.*')])])
async def auto_ban(app: GraiaMiraiApplication, group: Group, message: MessageChain, member:Member):
        ...
@bcc.receiver(GroupMessage,
    headless_decoraters = [Depend(test)],
    dispatchers = [Kanata([RegexMatch('test.*')])])
async def auto_ban(app: GraiaMiraiApplication, group: Group, message: MessageChain, member:Member):
        ...
@bcc.receiver(GroupMessage,
    headless_decoraters = [Depend(test)],
    dispatchers = [Kanata([RegexMatch('test.*')])])
async def auto_ban(app: GraiaMiraiApplication, group: Group, message: MessageChain, member:Member):
        ...
@bcc.receiver(GroupMessage,
    headless_decoraters = [Depend(test)],
    dispatchers = [Kanata([RegexMatch('test.*')])])
async def auto_ban(app: GraiaMiraiApplication, group: Group, message: MessageChain, member:Member):
        ...
@bcc.receiver(GroupMessage,
    headless_decoraters = [Depend(test)],
    dispatchers = [Kanata([RegexMatch('test.*')])])
async def auto_ban(app: GraiaMiraiApplication, group: Group, message: MessageChain, member:Member):
        ...
@bcc.receiver(GroupMessage,
    headless_decoraters = [Depend(test)],
    dispatchers = [Kanata([RegexMatch('test.*')])])
async def auto_ban(app: GraiaMiraiApplication, group: Group, message: MessageChain, member:Member):
        ...
@bcc.receiver(GroupMessage,
    headless_decoraters = [Depend(test)],
    dispatchers = [Kanata([RegexMatch('test.*')])])
async def auto_ban(app: GraiaMiraiApplication, group: Group, message: MessageChain, member:Member):
        ...
@bcc.receiver(GroupMessage,
    headless_decoraters = [Depend(test)],
    dispatchers = [Kanata([RegexMatch('test.*')])])
async def auto_ban(app: GraiaMiraiApplication, group: Group, message: MessageChain, member:Member):
        ...
@bcc.receiver(GroupMessage,
    headless_decoraters = [Depend(test)],
    dispatchers = [Kanata([RegexMatch('test.*')])])
async def auto_ban(app: GraiaMiraiApplication, group: Group, message: MessageChain, member:Member):
        ...
@bcc.receiver(GroupMessage,
    headless_decoraters = [Depend(test)],
    dispatchers = [Kanata([RegexMatch('test.*')])])
async def auto_ban(app: GraiaMiraiApplication, group: Group, message: MessageChain, member:Member):
        ...
@bcc.receiver(GroupMessage,
    headless_decoraters = [Depend(test)],
    dispatchers = [Kanata([RegexMatch('test.*')])])
async def auto_ban(app: GraiaMiraiApplication, group: Group, message: MessageChain, member:Member):
        ...


app.launch_blocking()