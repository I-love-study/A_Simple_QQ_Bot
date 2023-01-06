from typing import Optional, Literal, overload
import skia
import PIL.Image

Ink = str | int | tuple[int, int, int] | tuple[int, int, int, int]


def get_color(color: Ink) -> int:
    if isinstance(color, int):
        return color
    elif isinstance(color, str):
        c = getattr(skia, "Color" + color.upper())
        if isinstance(c, int):
            return c
        else:
            raise ValueError("Unknown Color name")
    else:
        return skia.Color(*color)

class MultiWriter:

    def __init__(self, size: int = 50, stroke_width: int = 0, width: int = 0, height: int = 0):
        self.fontmgr = skia.FontMgr()
        self.size = size
        self.width = width
        self.height = height
        self.stroke_width = stroke_width
        # 能从文件来就从文件来，从文件中来不了再从系统里随便找一个
        self.emoji_font = skia.Font(
            skia.Typeface.MakeFromFile("static/font/NotoColorEmoji.ttf")
            or self.fontmgr.matchFamilyStyleCharacter("monospace", skia.FontStyle(), ['zh-cn'],
                                                      ord('👴')), size)
        self.word_font = skia.Font(
            skia.Typeface.MakeFromFile("static/font/SourceHanSans-Medium.ttf")
            or self.fontmgr.matchFamilyStyleCharacter("monospace", skia.FontStyle(), ['zh-cn'],
                                                      ord('你')), size)
        self.builder = skia.TextBlobBuilder()

    def analyse_font(self, text: str):
        analyse = [[]]
        seek = 0 if self.height != 1 else self.word_font.measureText("...")
        height = 1

        for char in text:
            ord_char = ord(char)
            if self.word_font.unicharToGlyph(ord_char):
                select_font = self.word_font
            elif self.emoji_font.unicharToGlyph(ord_char):
                select_font = self.emoji_font
            else:
                select_font = skia.Font(self.fontmgr.matchFamilyStyleCharacter(
                    "monospace", skia.FontStyle(), ['zh-cn'],ord_char), self.size)

            char_size = select_font.measureText(char)
            if (self.width and seek + char_size > self.width) or char == "\n":
                height += 1
                if height == self.height:
                    analyse.append([])
                    seek = self.word_font.measureText("...")
                elif height == self.height + 1:
                    analyse[-1].append(["...", self.word_font])
                    break
                else:
                    analyse.append([])
                    seek = 0
                
                if char == "\n":
                    continue

            seek += char_size
            
            if analyse[-1] and analyse[-1][-1][1] == select_font:
                analyse[-1][-1][0] += char
            else:
                analyse[-1].append([char, select_font])            

        return analyse

    def build_textblob(self, analyse):
        height = self.size
        for line in analyse:
            seek = 0
            for word, font in line:
                self.builder.allocRun(word, font, seek, height)
                seek += font.measureText(word)
            height += self.size + self.stroke_width

    def text2pic(self, text: str, color: Ink = 0xFFFFFFFF, background_color: Optional[Ink] = None) -> skia.Image:
        analyse = self.analyse_font(text)
        self.build_textblob(analyse)
        blob = self.builder.make()
        rect = blob.bounds()

        width = self.width if self.width else int(rect.right())
        height = ((len(analyse) - 1) * (self.stroke_width + self.size) +
                  int(self.word_font.getSpacing()))

        surface = skia.Surface(width, height)
        canvas = surface.getCanvas()
        if background_color is not None:
            canvas.clear(get_color(background_color))
        paint = skia.Paint(AntiAlias=True, Color=get_color(color))
        canvas.drawTextBlob(blob, 0, 0, paint)
        return surface.makeImageSnapshot()

@overload
def text2pic(text: str,
             color: Ink = 0xFFFFFFFF,
             size: int = 50,
             stroke_width: int = 0,
             width: int = 0,
             height: int = 0,
             background_color: Optional[Ink] = None,
             ret_type:Literal["bytes"] = "bytes",
             image_type: str = "PNG",
             quality: int = 80) -> bytes:
    ...

@overload
def text2pic(text: str,
             color: Ink = 0xFFFFFFFF,
             size: int = 50,
             stroke_width: int = 0,
             width: int = 0,
             height: int = 0,
             background_color: Optional[Ink] = None,
             ret_type:Literal["skia"]= "skia") -> skia.Image:
    ...

@overload
def text2pic(text: str,
             color: Ink = "WHITE",
             size: int = 50,
             stroke_width: int = 0,
             width: int = 0,
             height: int = 0,
             background_color: Optional[Ink] = None,
             ret_type:Literal["PIL"] = "PIL") -> PIL.Image.Image:
    ...

def text2pic(text: str, # type: ignore
             color: Ink = "WHITE",
             size: int = 50,
             stroke_width: int = 0,
             width: int = 0,
             height: int = 0,
             background_color: Optional[Ink] = None,
             ret_type:Literal["skia", "PIL", "bytes"] = "skia",
             **kwargs):
    writer = MultiWriter(size, stroke_width, width, height)
    image = writer.text2pic(text, color, background_color)
    if ret_type == "skia":
        return image
    elif ret_type == "PIL":
        return PIL.Image.fromarray(image, 'RGBa') # type: ignore
    elif ret_type == "bytes":
        image_type = getattr(skia.EncodedImageFormat, "k" + kwargs.get("image_type", "PNG").upper())
        quality = kwargs.get("quality", 80)
        return image.encodeToData(image_type, quality).bytes()

if __name__ == "__main__":
    text = ("👴哭了"*10 + "\n")*10
    print(len(text))
    import time
    a = MultiWriter(stroke_width=10, width=1700)
    t = time.time()
    b = a.text2pic(text).encodeToData(skia.kPNG, 100).bytes()
    print(time.time() - t)
    with open("test.png", "wb") as f:
        f.write(b)
