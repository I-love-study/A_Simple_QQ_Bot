import asyncio
from graia.broadcast import Broadcast
from graia.application import GraiaMiraiApplication, Session
from graia.broadcast.interrupt import InterruptControl
import graia.scheduler

import logging
logging.basicConfig(format="[%(asctime)s][%(levelname)s]: %(message)s", level=logging.INFO)

from .modules import *
from .judge import *

def init(config_session: Session) -> None:
    global bcc, sche, app, inc
    loop = asyncio.get_event_loop()
    bcc = Broadcast(loop = loop, debug_flag = True)
    sche = graia.scheduler.GraiaScheduler(loop = loop, broadcast = bcc)
    inc = InterruptControl(bcc)
    app = GraiaMiraiApplication(
        broadcast=bcc,
        connect_info=config_session,
        logger=logging.getLogger('graia'),
        group_message_log_format = '[{group_name}] {member_name}({member_permission}) -> {message_string}'
    )

trans_data = {}
def trans(**kwargs) -> None:
    global trans_data
    trans_data = kwargs

class get:
    @staticmethod
    def app() -> GraiaMiraiApplication:
        if app is None:
            raise ValueError('GraiaMiraiApplication 实例尚未初始化')
        return app
    @staticmethod
    def bcc() -> Broadcast:
        if bcc is None:
            raise ValueError('Broadcast 实例尚未初始化')
        return bcc
    @staticmethod
    def sche() -> graia.scheduler.GraiaScheduler:
        if bcc is None:
            raise ValueError('Scheduler 实例尚未初始化')
        return sche
    @staticmethod
    def inc() -> InterruptControl:
        if inc is None:
            raise ValueError('InterruptControl 实例尚未初始化')
        return inc
    @staticmethod
    def trans(get) -> Any:
        return trans_data[get]