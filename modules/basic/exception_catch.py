from graia.ariadne.app import Ariadne

from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image
from graia.broadcast.builtin.event import ExceptionThrowed
from graia.saya import Saya, Channel
from graiax.shortcut.saya import listen
from rich.traceback import Traceback
from rich.console import Console
from rich.terminal_theme import MONOKAI

from playwright.async_api import async_playwright
from io import StringIO
import traceback

saya = Saya.current()
channel = Channel.current()

CONSOLE_SVG_FORMAT = """\
<svg class="rich-terminal" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
    <!-- Generated with Rich https://www.textualize.io -->
    <style>

    @font-face {{
        font-family: "Fira Code";
        src: local("FiraCode-Regular"),
                url("https://cdnjs.cloudflare.com/ajax/libs/firacode/6.2.0/woff2/FiraCode-Regular.woff2") format("woff2"),
                url("https://cdnjs.cloudflare.com/ajax/libs/firacode/6.2.0/woff/FiraCode-Regular.woff") format("woff");
        font-style: normal;
        font-weight: 400;
    }}
    @font-face {{
        font-family: "Fira Code";
        src: local("FiraCode-Bold"),
                url("https://cdnjs.cloudflare.com/ajax/libs/firacode/6.2.0/woff2/FiraCode-Bold.woff2") format("woff2"),
                url("https://cdnjs.cloudflare.com/ajax/libs/firacode/6.2.0/woff/FiraCode-Bold.woff") format("woff");
        font-style: bold;
        font-weight: 700;
    }}

    .{unique_id}-matrix {{
        font-family: Fira Code, 思源黑体, monospace;
        font-size: {char_height}px;
        line-height: {line_height}px;
        font-variant-east-asian: full-width;
    }}

    .{unique_id}-title {{
        font-size: 18px;
        font-weight: bold;
        font-family: arial;
    }}

    {styles}
    </style>

    <defs>
    <clipPath id="{unique_id}-clip-terminal">
      <rect x="0" y="0" width="{terminal_width}" height="{terminal_height}" />
    </clipPath>
    {lines}
    </defs>

    {chrome}
    <g transform="translate({terminal_x}, {terminal_y})" clip-path="url(#{unique_id}-clip-terminal)">
    {backgrounds}
    <g class="{unique_id}-matrix">
    {matrix}
    </g>
    </g>
</svg>
"""

async def make_pic(event: ExceptionThrowed):
    c = Console(file=StringIO(), record=True)
    t = Traceback.from_exception(
        type(event.exception),
        event.exception,
        event.exception.__traceback__,
        show_locals=True,
    )
    c.print(t)
    content = c.export_svg(title="报错のtraceback", code_format=CONSOLE_SVG_FORMAT)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(device_scale_factor=2.0)
        page = await context.new_page()
        await page.set_content(content)
        pic = await page.screenshot(type="png", full_page=True)
    return pic

@listen(ExceptionThrowed)
async def exception_catch(event: ExceptionThrowed):
    
    print(event.event)
    if not isinstance(event.event, ExceptionThrowed):
        app: Ariadne = Ariadne.current()
        await app.send_group_message(
            saya.access('all_setting')['admin_group'],
            MessageChain(Image(data_bytes=await make_pic(event)))
        )


def test_function(a, b):
    return a / b

from graia.ariadne.event.message import GroupMessage
from graia.ariadne.model import Member
from graia.ariadne.message.chain import MessageChain
@listen(GroupMessage)
async def test(app: Ariadne, member: Member, msg: MessageChain):
    if member.id == 1450069615 and str(msg) == "test":
        test_function(1, 0)