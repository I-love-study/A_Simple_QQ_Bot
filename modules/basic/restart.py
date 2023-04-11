import atexit
import os
import platform
import time
from pathlib import Path
from typing import Union

from creart import create
from graia.ariadne.app import Ariadne
from graia.ariadne.event.lifecycle import ApplicationLaunch
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.parser.base import MatchContent
from graia.ariadne.model import Group, Member
from graia.broadcast.interrupt import InterruptControl
from graia.broadcast.interrupt.waiter import Waiter
from graia.saya import Channel, Saya
from graiax.shortcut.saya import decorate, listen

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

@atexit.register
def detect_restart():
    if is_restart and platform.system() == 'Linux' and os.environ.get("TMUX"):
        # 通过 send keys 让他能够自动关闭 windows
        os.system("tmux select-pane -U; tmux send-keys exit Enter")

@listen(GroupMessage)
@decorate(decorators.config_check(active_members=saya.access('all_setting')['ultra_administration']))
@decorate(MatchContent("重启"))
async def restart(app: Ariadne, group: Group, message: MessageChain, member:Member):
    global is_restart
    await app.send_group_message(group, MessageChain('确定要重启机器人吗(是/否)'))
    get = await inc.wait(GroupMessageInterrupt(group, member))
    if str(get) != '是':
        await app.send_message(group, MessageChain("已取消"))
        return
    
    os.system('git pull')
    Path('restart_time').write_text(f'{group.id}|{time.time()}', encoding='UTF-8')
    if platform.system() == 'Windows':
        os.system('start /i /max main.py')
    elif platform.system() == 'Linux' and os.environ.get("TMUX"):
        os.system(f'tmux split-window -c {Path().absolute()} "pdm run python main.py; $SHELL"')
        is_restart = True
    elif platform.system() == "MACOS":
        await app.send_group_message(group, MessageChain('我不会，长大后再学吧'))
        return
    else:
        await app.send_group_message(group, MessageChain('警告，你的环境没有用TMUX需要手动启动'))
        return
    app.stop()
    exit()

@listen(ApplicationLaunch)
async def check_restart(app: Ariadne):
    restart_path = Path('restart_time')
    if restart_path.is_file():
        g, t = restart_path.read_text(encoding='UTF-8').split('|')
        await app.send_group_message(int(g), MessageChain(
            f'重启成功,共耗时{time.time()-float(t):0.2f}秒'.format()
            ))
        restart_path.unlink()