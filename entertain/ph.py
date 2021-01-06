from graia.application import GraiaMiraiApplication
from graia.application.event.messages import GroupMessage
from graia.application.message.elements.internal import *
from graia.application.message.chain import MessageChain
from graia.application.message.parser.kanata import Kanata
from graia.application.message.parser.signature import FullMatch, RequireParam
from graia.application.group import Group, Member

from core import judge
from core import get
from PIL import Image as IMG, ImageFont, ImageDraw
from io import BytesIO
import shlex

def make_porn_logo(left: str, right: str,font_size: int):
	ttf = ImageFont.truetype('lib/SourceHanSans22.ttf', font_size)
	gap = int(font_size/4)
	r_wide,r_height = ttf.getsize(right)
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
	yellow_draw.text((gap,gap/2), right, font=ttf, fill=(0,0,0))#gap/2是为了去除此字体本身有的空隙
	#画黑色背景
	l_wide,l_height = ttf.getsize(left)
	main_size = yellow_size[0]+l_wide+gap*3, yellow_size[1]+gap*2
	black_background = IMG.new("RGBA", main_size, (0,0,0))
	black_draw = ImageDraw.Draw(black_background)
	#写白色文字
	black_draw.text((gap,gap*3/2), left, font=ttf, fill=(255,255,255))
	#粘贴黄图
	black_background.paste(yellow_background, (l_wide+gap*2, gap))
	ret = BytesIO()
	black_background.save(ret, format='PNG')
	return ret.getvalue()

bcc = get.bcc()
@bcc.receiver(GroupMessage, headless_decoraters = [judge.group_check(__name__)],
							dispatchers = [Kanata([FullMatch('ph'), RequireParam('para')])])
async def pornhub(app: GraiaMiraiApplication, group: Group, member: Member, para: MessageChain):
	if len(tag:=shlex.split(para.asDisplay())) == 2:
		pic = make_porn_logo(*tag, 120)
		msg = [Image.fromUnsafeBytes(pic)]
	else:
		msg = [Plain('消息有误，请重试')]
	await app.sendGroupMessage(group, MessageChain.create(msg))