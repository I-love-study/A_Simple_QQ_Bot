import asyncio
from pathlib import Path

import yaml
from graia.saya import Saya
from graia.broadcast import Broadcast
from graia.scheduler import GraiaScheduler
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.saya.builtins.broadcast import BroadcastBehaviour
from graia.scheduler.saya.behaviour import GraiaSchedulerBehaviour
from graia.ariadne.app import Ariadne
from graia.ariadne.model import MiraiSession

import decorators
from orm import *

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
bcc = Broadcast(loop=loop)
sche = GraiaScheduler(loop = loop, broadcast = bcc)
saya = Saya(bcc)
saya.install_behaviours(BroadcastBehaviour(bcc))
saya.install_behaviours(GraiaSchedulerBehaviour(sche))

with open('configs.yml', encoding='UTF-8') as f:
    configs = yaml.safe_load(f)

app = Ariadne(
    broadcast=bcc,
    connect_info=MiraiSession(
        host=configs['miraiHost'],
        account=configs['account'],
        verify_key=configs["verify_key"],
    )
)


with saya.module_context():
    group_setting = {}
    saya.require('setting')
    import setting
    saya.mount('all_setting', configs)
    saya.mount('group_setting', setting.GetSetting())
    for module_dir in configs['load_modules_folder']:
        module_dir = Path(module_dir)
        prefix = '.'.join(module_dir.parts)
        for module in module_dir.iterdir():
            if any((
              module.name.startswith('_'),
              module.is_file() and module.suffix != '.py',
              module.is_dir() and not (module / '__init__.py').exists())):
                continue
            config_check_deco = decorators.ConfigCheck(prefix, module.stem)
            if not session.query(session.query(Module).filter_by(folder=prefix, name=module.stem).exists()).scalar():
                a = [ModuleSetting(switch=True, group_id=g.id) for g in session.query(QQGroup).all()]
                session.add_all(a)
                session.add(Module(folder=prefix, name=module.stem, setting=a))
                #现在给赶紧commit了要不然要是有插件要数据就完蛋了
                session.commit()
            for cube in saya.require(f"{prefix}.{module.stem}").content:
                if isinstance(cube.metaclass, ListenerSchema):
                    cube_deco = cube.metaclass.decorators
                    if not (decorators.SettingCheck in [type(a) for a in cube_deco] and
                      next(a for a in cube_deco if isinstance(a, decorators.SettingCheck)).out_control):
                        cube_deco.append(config_check_deco)
                        (saya.broadcast.getListener(cube.content)
                             .decorators.append(config_check_deco))

if __name__ == '__main__':
    loop.run_until_complete(app.lifecycle())