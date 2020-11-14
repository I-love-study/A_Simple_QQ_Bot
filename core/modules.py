from graia.application.logger import LoggingLogger
from pathlib import Path
import importlib
from typing import Any

loaded_plugins = set()
plugin_dir_setting = set()

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

class Plugin_dir:
    __slots__ = ('dir_name', 'active_groups', 'negative_groups',
        'active_members','negative_members')

    def __init__(self, dir_name, active_groups, negative_groups,
        active_members,negative_members):
        self.dir_name = dir_name
        self.active_groups = active_groups
        self.negative_groups = negative_groups
        self.active_members = active_members
        self.negative_members = negative_members

def load_plugins(plugin_dir: Path,
    active_groups: list = [],
    negative_groups: list = [],
    active_members: list = [],
    negative_members: list = []
    ) -> int:
    '''本函数负责导入文件夹内的插件
    plugin_dir是导入的文件夹（请使用相对位置）
    active_groups是判断群的，negative_groups同理'''
    count = 0
    plugin_dir_setting.add(Plugin_dir(
        '.'.join(plugin_dir.parts), 
        active_groups, negative_groups, 
        active_members,negative_members))
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



