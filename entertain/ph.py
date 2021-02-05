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
from fontTools.ttLib import TTFont
from io import BytesIO
import shlex

def words2img(words, color, size):
	word_ttf  = ImageFont.truetype('src/font/SourceHanSans-Heavy.otf', size)
	word_use  = TTFont('src/font/SourceHanSans-Heavy.otf')['cmap'].tables[0].ttFont.getBestCmap()
	emoji_ttf = ImageFont.truetype('src/font/NotoColorEmoji.ttf', size)
	emoji_use = TTFont('src/font/NotoColorEmoji.ttf')['cmap'].tables[0].ttFont.getBestCmap()
	use = []
	for a in words:
		o = ord(a)
		if o in word_use:
			ty = word_ttf
			gap = int(size/8)
		elif o in emoji_use:
			ty = emoji_ttf
			gap = 0
		else:
			raise ValueError

		if use and use[-1]['type'] is ty:
			use[-1]['words'] += a
		else:
			use.append({'words': a,'type' : ty, 'gap': gap})

	all_size = [word['type'].getsize(word['words']) for word in use]
	height = max(w[1] for w in all_size)
	length = sum(w[0] for w in all_size)

	background = IMG.new("RGBA", (length, height), (0,0,0,0))
	draw = ImageDraw.Draw(background)
	start_x = 0
	for w, s in zip(use, all_size):
		y = int((height-s[1])/2)
		draw.text((start_x, y-w['gap']), w['words'], font=w['type'], fill=color, embedded_color=True)
		start_x += s[0]

	return background

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
	main_size = yellow_size[0]+l_wide+gap*3, yellow_size[1]+gap*2
	black_background = IMG.new("RGBA", main_size, (0,0,0))
	#写白色文字
	black_background.paste(left_font, (gap,gap*2), mask=left_font)
	#粘贴黄图
	black_background.paste(yellow_background, (l_wide+gap*2, gap))
	ret = BytesIO()
	black_background.save(ret, format='PNG')
	return ret.getvalue()

bcc = get.bcc()
@bcc.receiver(GroupMessage, headless_decoraters = [judge.config_check(__name__)],
							dispatchers = [Kanata([FullMatch('ph'), RequireParam('para')])])
async def pornhub(app: GraiaMiraiApplication, group: Group, member: Member, para: MessageChain, message: MessageChain):
	if len(tag:=shlex.split(para.asDisplay())) == 2:
		pic = make_porn_logo(*tag, 109)#必须是109(emoji)
		msg = [Image.fromUnsafeBytes(pic)]
	else:
		msg = [Plain('消息有误，请重试')]
	await app.sendGroupMessage(group, MessageChain.create(msg))