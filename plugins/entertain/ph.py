from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import *
from graia.ariadne.message.parser.twilight import Twilight, MatchResult
from graia.ariadne.model import Group, Member
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

from expand.text import EmojiWriter
from PIL import Image as IMG, ImageDraw
from io import BytesIO
import shlex

words2img = EmojiWriter().text2pic
channel = Channel.current()

channel.name("PornHubStyleWord")
channel.description("发送'ph [字] [字]'获取熟悉的ph图标")
channel.author("I_love_study")

@channel.use(ListenerSchema(
    listening_events=[GroupMessage],
    inline_dispatchers=[Twilight.from_command("ph {l} {r}")]
))
async def pornhub(app: Ariadne, group: Group, l: MatchResult, r: MatchResult):
    pic = make_porn_logo(l.result.display, r.result.display, 109) # 必须是109(emoji)
    await app.send_group_message(group, MessageChain(Image(data_bytes=pic)))

def make_porn_logo(left: str, right: str,font_size: int):
    gap = int(font_size/4)
    right_font = words2img(right, (0,0,0), font_size)
    r_wide,r_height = right_font.size
    yellow_color = '#F7971D'
    yellow_size = r_wide+gap*2, r_height+gap*2
    yellow_background = IMG.new("RGBA", yellow_size, (0,0,0))
    yellow_draw = ImageDraw.Draw(yellow_background)
    #画出黄色圆角矩形ing
    yellow_draw.ellipse((0,0,gap*2,gap*2),fill=yellow_color)
    yellow_draw.ellipse((r_wide,0,yellow_size[0],gap*2),fill=yellow_color)
    yellow_draw.ellipse((0,r_height,gap*2,yellow_size[1]),fill=yellow_color)
    yellow_draw.ellipse((r_wide,r_height,*yellow_size),fill=yellow_color)
    yellow_draw.rectangle((0,gap,yellow_size[0],yellow_size[1]-gap),fill=yellow_color)
    yellow_draw.rectangle((gap,0,yellow_size[0]-gap,yellow_size[1]),fill=yellow_color)
    #写文字
    yellow_background.paste(right_font, (gap,gap), mask=right_font)#gap/2是为了去除此字体本身有的空隙
    #画黑色背景
    left_font = words2img(left, (255,255,255), font_size)
    l_wide,l_height = left_font.size
    main_size = yellow_size[0]+l_wide+gap*3, max(yellow_size[1]+gap*2, l_height+gap*2)
    black_background = IMG.new("RGBA", main_size, (0,0,0))
    #写白色文字
    y = int((main_size[1]-l_height)/2)
    black_background.paste(left_font, (gap,y), mask=left_font)
    #粘贴黄图
    y = int((main_size[1]-yellow_size[1])/2)
    black_background.paste(yellow_background, (l_wide+gap*2, y))
    black_background.save(ret := BytesIO(), format='PNG')
    return ret.getvalue()