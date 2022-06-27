import asyncio
import pkgutil
from pathlib import Path

import yaml
from graia.ariadne.app import Ariadne
from graia.ariadne.console import Console
from graia.ariadne.console.saya import ConsoleBehaviour
from graia.ariadne.connection.config import config, HttpClientConfig, WebsocketClientConfig
from graia.broadcast import Broadcast
from graia.saya import Saya
from graia.saya.builtins.broadcast import BroadcastBehaviour
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.scheduler import GraiaScheduler
from graia.scheduler.saya.behaviour import GraiaSchedulerBehaviour
from graia.scheduler.saya.schema import SchedulerSchema

import decorators
from orm import *

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
bcc = Broadcast(loop=loop)
con = Console(broadcast=bcc, prompt="SimpleBot> ")
sche = GraiaScheduler(loop=loop, broadcast=bcc)
Ariadne.config(loop=loop, broadcast=bcc)
saya = Saya(bcc)
saya.install_behaviours(
    BroadcastBehaviour(bcc),
    ConsoleBehaviour(con),
    GraiaSchedulerBehaviour(sche),
)

with open('configs.yml', encoding='UTF-8') as f:
    configs = yaml.safe_load(f)

app = Ariadne(
    config(
        # host=configs['miraiHost'],
        configs['account'],
        configs["verify_key"],
        HttpClientConfig(configs['miraiHost']),
        WebsocketClientConfig(configs['miraiHost']),
    )
)


with saya.module_context():
    group_setting = {}
    saya.require('setting')
    import setting
    saya.mount('all_setting', configs)
    saya.mount('group_setting', setting.GetSetting())
    for module_dir in configs['load_modules_folder']:
        dir_name = ".".join(Path(module_dir).parts)
        for module in pkgutil.iter_modules([module_dir]):
            if module.name.startswith("_"):
                continue
            command = session.query(Module).filter_by(folder=dir_name, name=module.name).exists()
            if not session.query(command).scalar():
                a = [ModuleSetting(switch=True, group_id=g.id) for g in session.query(QQGroup).all()]
                session.add_all(a)
                session.add(Module(folder=dir_name, name=module.name, setting=a))
                #现在给赶紧commit了要不然要是有插件要数据就完蛋了
                session.commit()

            config_check_deco = decorators.ConfigCheck(dir_name, module.name)
            config_check_deco_sche = decorators.ConfigCheck(dir_name, module.name, True)
            for cube in saya.require(f"{dir_name}.{module.name}").content:
                if isinstance(cube.metaclass, ListenerSchema):
                    cube_deco = cube.metaclass.decorators
                    deco = next((a for a in cube_deco if isinstance(a, decorators.SettingCheck)), None)
                    if deco is None or not deco.out_control:
                        cube_deco.append(config_check_deco)
                        saya.broadcast.getListener(cube.content).decorators.append(config_check_deco)
                elif isinstance(cube.metaclass, SchedulerSchema):
                    cube.metaclass.decorators.append(config_check_deco_sche)
                    next(s for s in sche.schedule_tasks
                         if s.target == cube.content).decorators.append(config_check_deco_sche)

if __name__ == '__main__':
    app.launch_blocking()