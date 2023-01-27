from graia.ariadne.app import Ariadne

from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image
from graia.broadcast.builtin.event import ExceptionThrowed
from graia.saya import Saya, Channel
from graiax.shortcut.saya import listen

from io import StringIO
import traceback
from utils.text import text2pic

saya = Saya.current()
channel = Channel.current()

async def make_pic(event):
    with StringIO() as fp:
        traceback.print_tb(event.exception.__traceback__, file=fp)
        tb = fp.getvalue()
    output = (
        f"异常事件：\n{event.event}\n"
        f"异常内容：\n{event.exception}\n"
        f"异常回滚：\n{tb}"
    )
    return text2pic(str(output), 0xFFFFFFFF, 40, 5, 3200, 0xFF000000, "bytes")

@listen(ExceptionThrowed)
async def exception_catch(event: ExceptionThrowed):
    if not isinstance(event.event, ExceptionThrowed):
        app: Ariadne = Ariadne.current()
        await app.send_group_message(
            saya.access('all_setting')['admin_group'],
            MessageChain(Image(data_bytes=await make_pic(event)))
        )