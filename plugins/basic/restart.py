from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.event.lifecycle import ApplicationLaunched
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import *
from graia.ariadne.message.parser.twilight import Twilight, FullMatch
from graia.ariadne.model import Group, Member
from graia.broadcast.interrupt import InterruptControl
from graia.broadcast.interrupt.waiter import Waiter
from graia.broadcast.exceptions import ExecutionStop
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

from pathlib import Path
import platform
import time
import os

import decorators

saya = Saya.current()
channel = Channel.current()
inc = InterruptControl(saya.broadcast)

class GroupMessageInterrupt(Waiter.create([GroupMessage])):

    def __init__(self, group: Union[Group, int], member: Union[Member, int]):
        self.group = group if isinstance(group, int) else group.id
        self.member = member if isinstance(member, int) else member.id

    async def detected_event(self, group: Group, member: Member, message: MessageChain):
        if self.group == group.id and self.member == member.id:
            return message

@channel.use(ListenerSchema(
    listening_events=[GroupMessage],
    decorators=[decorators.config_check(active_members=[1450069615,2480328821])],
    inline_dispatchers=[Twilight([FullMatch("重启")])]
    ))
async def restart(app: Ariadne, group: Group, message: MessageChain, member:Member):
    await app.sendGroupMessage(group, MessageChain.create([
        Plain(f'确定要重启机器人吗(是/否)')]))
    get = await inc.wait(GroupMessageInterrupt(group, member))
    if get.messageChain.asDisplay() == '是':
        os.system('git pull')
        Path('restart_time').write_text(f'{group.id}|{time.time()}', encoding='UTF-8')
        if platform.system() == 'Windows':
            os.system('start /i /max main.py')
            await app.shutdown()
            exit()
        elif platform.system() == 'Linux':
            await app.sendGroupMessage(group, MessageChain.create([
                Plain(f'警告，现阶段Linux需要手动启动')]))
            await app.shutdown()
            exit()

@channel.use(ListenerSchema(listening_events=[ApplicationLaunched]))
async def check_restart(app: Ariadne):
    restart_path = Path('restart_time')
    if restart_path.is_file():
        g, t = restart_path.read_text(encoding='UTF-8').split('|')
        await app.sendGroupMessage(int(g), MessageChain.create([
            Plain('重启成功,共耗时{:0.2f}秒'.format(time.time()-float(t)))
            ]))
        restart_path.unlink()