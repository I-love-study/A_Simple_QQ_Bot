import asyncio
from graia.broadcast import Broadcast
from graia.application import GraiaMiraiApplication, Session

import graia.scheduler
from graia.scheduler import timers

from graia.application.logger import LoggingLogger
from pathlib import Path

import importlib
from typing import Any

loaded_plugins = set()

trans_data = {}

class Plugin:
    __slots__ = ('module', 'name', 'usage')

    def __init__(self, module, name = None, usage = None):
        self.module = module
        self.name = name
        self.usage = usage

def load_plugin(module_name: Path) -> bool:
    try:
        module = importlib.import_module(module_name)
        name = getattr(module, '__plugin_name__', None)
        usage = getattr(module, '__plugin_usage__', None)
        loaded_plugins.add(Plugin(module, name, usage))
        LoggingLogger().info(f'成功导入 "{module_name}"')
        return True
    except Exception as e:
        print(e)
        LoggingLogger().error(f'导入失败 "{module_name}", error: {e}')
        #logger.exception(e)
        return False

def load_plugins(plugin_dir: Path) -> int:
    count = 0
    for path in plugin_dir.iterdir():
        if path.name.startswith('_'):
            continue
        if path.is_file() and path.suffix != '.py':
            continue
        if path.is_dir() and not (path / '__init__.py').exists():
            continue
        if load_plugin(f'{".".join(plugin_dir.parts)}.{path.stem}'):
            count += 1
    LoggingLogger().info(f'共导入了 {count} 个插件')
    return count

def init(config_session: Session) -> None:
    global bcc, sche, app
    loop = asyncio.get_event_loop()
    bcc = Broadcast(loop = loop, debug_flag = True)
    sche = graia.scheduler.GraiaScheduler(loop = loop, broadcast = bcc)
    app = GraiaMiraiApplication(
        broadcast = bcc,
        connect_info = config_session
    )

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
    def trans(get) -> Any:
        return trans_data[get]