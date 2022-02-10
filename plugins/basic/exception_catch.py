from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import *
from graia.broadcast.builtin.event import ExceptionThrowed
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

from io import StringIO, BytesIO
import traceback
from PIL import ImageFont, ImageDraw, Image as IMG
from expand.text import analyse_font

saya = Saya.current()
channel = Channel.current()

font = ImageFont.truetype('src/font/SourceHanSansHW-Regular.otf', 20)

async def make_pic(event):
    with StringIO() as fp:
        traceback.print_tb(event.exception.__traceback__, file=fp)
        tb = fp.getvalue()

    output = (
        f"异常事件：\n{event.event}\n",
        f"异常内容：\n{event.exception}\n",
        f"异常回滚：\n{tb}"
    )

    new_output = analyse_font(2000, output, font)
    img = IMG.new("RGB", font.getsize(new_output), (0, 0, 0))
    ImageDraw.Draw(img).text((0, 0), new_output, fill="black", font=font)
    img.save(out := BytesIO(), format="JPEG")
    return out.getvalue()


@channel.use(ListenerSchema(listening_events=[ExceptionThrowed]))
async def exception_catch(app: Ariadne, event):
    if isinstance(event.event, ExceptionThrowed):
        return
    else:
        await app.sendGroupMessage(
            saya.access('all_setting')['admin_group'],
            MessageChain.create(Image(data_bytes=make_pic(event)))
        )
