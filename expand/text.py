from PIL import ImageDraw, ImageFont, Image as IMG
from fontTools.ttLib import TTFont

#防止创建多个类时内存跟你看到这些代码时候的血压一样UpUp
#因为emoji只能支持109的size嘛。。。
word_ttf  = ImageFont.truetype('src/font/SourceHanSans-Heavy.otf', 109)
word_use  = set(TTFont('src/font/SourceHanSans-Heavy.otf')['cmap'].tables[0].ttFont.getBestCmap())
emoji_ttf = ImageFont.truetype('src/font/NotoColorEmoji.ttf', 109)
emoji_use = set(TTFont('src/font/NotoColorEmoji.ttf')['cmap'].tables[0].ttFont.getBestCmap())

class EmojiWriter:
	"""此类用于绘制包含emoji的字符串"""

	def __init__(self):
		global emoji_ttf, emoji_use, word_ttf, word_use
		self.word_ttf = word_ttf
		self.word_use = word_use
		self.emoji_ttf = emoji_ttf
		self.emoji_use = emoji_use

	def analyze(self, text):
		return [self._analyze(line) for line in text.splitlines()]

	def _analyze(self, text):
		use = []
		for a in self._single_character_analyze(text):
			if use and use[-1]['type'] is a['type']:
				use[-1]['words'] += a['words']
			else:
				use.append(a)
		return use

	def _single_character_analyze(self, text):
		for a in text:
			o = ord(a)
			if o in self.word_use:
				ty = self.word_ttf
				gap = int(109/8)
			elif o in self.emoji_use:
				ty = self.emoji_ttf
				gap = 0
			else:
				raise ValueError('Unknown_font')
			yield {'words': a,'type' : ty, 'gap': gap}

	def _steady_width_split(self, text, size, width):
		new_analysis = []
		now_width = 0
		wid = width*109/size
		analysis = [self._single_character_analyze(text) for line in text.splitlines()]
		for line in analysis:
			line_analysis = [[]]
			for char in line:
				char_width = char['type'].getsize(char['words'])[0]
				now_width += char_width
				if now_width > wid:
					line_analysis.append([])
					now_width = char_width
				if line_analysis[-1] and line_analysis[-1][-1]['type'] is char['type']:
					line_analysis[-1][-1]['words'] += char['words']
				else:
					line_analysis[-1].append(char)
			now_width = 0
			new_analysis.extend(line_analysis)
		return new_analysis

	def get_size(self, text='', size=None, stroke_width=0, width=None, use=None):
		"""获取字体大小"""
		if use is None:
			use = self._steady_width_split(text, size, width) if width else self.analyze(text)
		data = [self._get_size(size, line) for line in use]
		if len(data) == 1:
			return data[0]
		else:
			l = int(max(a[0] for a in data))
			h = int(sum(a[1] for a in data) + stroke_width*(len(data)-1))
			return (l, h)

	def _get_size(self, size, use, width=None):
		all_size = [word['type'].getsize(word['words']) for word in use]
		height = max(w[1] for w in all_size)
		length = sum(w[0] for w in all_size)
		toint = lambda x: int(x*(size or self.size)/109)
		return tuple(map(toint, (length, height)))

	def text2pic(self, text, color, size=None, stroke_width=0, width=None):
		"""将文本转换为图片(支持emoji，指定宽度等)
		注：因为emoji字体大小只能109，所以size会先等比放大size和wide再resize回来
		其中可能有些width会变大/变小"""
		use = self._steady_width_split(text, size, width) if width else self.analyze(text)
		all_size = [[word['type'].getsize(word['words']) for word in line] for line in use]
		font_height = int(max(char[1] for line in all_size for char in line)+(stroke_width*109/size))
		length, height = self.get_size('', 109, stroke_width*109/size, width=width,use=use)
		if width: length = int(width*109/size)

		background = IMG.new("RGBA", (length, height), (0,0,0,0))
		draw = ImageDraw.Draw(background)
		start_x, start_y = 0, 0
		for line, line_size in zip(use, all_size):
			for w, s in zip(line, line_size):
				draw.text((start_x, start_y-w['gap']), w['words'],
					font=w['type'], fill=color, embedded_color=w['type'] is emoji_ttf)
				start_x += s[0]
			start_y += font_height
			start_x = 0

		return background.resize(map(lambda x:int(x*size/109), background.size), IMG.ANTIALIAS)