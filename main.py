import core
from pathlib import Path
from graia.application import Session

if __name__ == '__main__':
    core.init(Session(
        host = "http://localhost:8070", # 填入 httpapi 服务运行的地址
        authKey = "I_Love_Study", # 填入 authKey
        account = 1145141919810, # 你的机器人的 qq 号
        websocket = True, # Graia 已经可以根据所配置的消息接收的方式来保证消息接收部分的正常运作.
        debug_flag = True
        )
    )
    core.load_plugins(Path('entertain'), active_groups = [1009529133,904763352])
    app = core.get.app()
    while True:
        try:
            app.launch_blocking()
        except KeyboardInterrupt:
            break