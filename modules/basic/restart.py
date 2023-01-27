from creart import create
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.event.lifecycle import ApplicationLaunched
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.parser.base import MatchContent
from graia.ariadne.model import Group, Member
from graia.broadcast.interrupt import InterruptControl
from graia.broadcast.interrupt.waiter import Waiter
from graia.saya import Saya, Channel
from graiax.shortcut.saya import listen, decorate

from typing import Union
from pathlib import Path
import platform
import time
import os

import decorators

saya = Saya.current()
channel = Channel.current()
inc = create(InterruptControl)

class GroupMessageInterrupt(Waiter.create([GroupMessage])):

    def __init__(self, group: Union[Group, int], member: Union[Member, int]):
        self.group = group if isinstance(group, int) else group.id
        self.member = member if isinstance(member, int) else member.id

    async def detected_event(self, group: Group, member: Member, message: MessageChain):
        if self.group == group.id and self.member == member.id:
            return message

@listen(GroupMessage)
@decorate(decorators.config_check(active_members=[1450069615,2480328821]))
@decorate(MatchContent("重启"))
async def restart(app: Ariadne, group: Group, message: MessageChain, member:Member):
    await app.send_group_message(group, MessageChain('确定要重启机器人吗(是/否)'))
    get = await inc.wait(GroupMessageInterrupt(group, member))
    if get.message_chain.display == '是':
        os.system('git pull')
        Path('restart_time').write_text(f'{group.id}|{time.time()}', encoding='UTF-8')
        if platform.system() == 'Windows':
            os.system('start /i /max main.py')
            app.stop()
            exit()
        elif platform.system() == 'Linux':
            await app.send_group_message(group, MessageChain('警告，现阶段Linux需要手动启动'))
            app.stop()
            exit()

@listen(ApplicationLaunched)
async def check_restart(app: Ariadne):
    restart_path = Path('restart_time')
    if restart_path.is_file():
        g, t = restart_path.read_text(encoding='UTF-8').split('|')
        await app.send_group_message(int(g), MessageChain(
            f'重启成功,共耗时{time.time()-float(t):0.2f}秒'.format()
            ))
        restart_path.unlink()