import imageio
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageFont, ImageDraw, ImageFilter, ImageOps

font_path = Path("static") / "font"

cjk_font_path = str(font_path / "字魂59号-创粗黑.ttf")
ascii_font_path = str(font_path / "Alte DIN 1451 Mittelschrift gepraegt Regular.ttf")

class CountDownImage:

    def __init__(self,
                 front: str,
                 start: str,
                 time: int | str,
                 end: str,
                 bottom: str,
                 rgba: bool = True,
                 gif: bool = False):
        self.front = front
        self.start = start
        self.time = time
        self.end = end
        self.bottom = bottom
        self.rgba = rgba
        self.gif = gif

    def create_background(self) -> None:
        word_font = ImageFont.truetype(cjk_font_path, 36)
        front_size = word_font.getbbox(self.front)
        start_size = word_font.getbbox(self.start)
        head_length = max(front_size[2], start_size[2] + 10)

        time_font = ImageFont.truetype(ascii_font_path, 90)
        if isinstance(self.time, int) and self.gif:
            time_size = max(time_font.getbbox(str(i))[2] for i in range(1, self.time + 1))
        elif isinstance(self.time, str) and self.gif:
            raise ValueError("can not be gif if time is string")
        else:
            time_size = time_font.getbbox(str(self.time))[2]
        self.time_size = time_size

        end_size = word_font.getbbox(self.end)[2:]

        bottom_font = ImageFont.truetype(ascii_font_path, 18)
        #getbbox 不能 multiline 555~
        bottom_size = ImageDraw.Draw(Image.new("1", (1, 1))).multiline_textbbox((0, 0), self.bottom,
                                                                                bottom_font)[2:]

        self.pic = Image.new("RGBA", (max(head_length + time_size + end_size[0],
                                          head_length - start_size[2] + bottom_size[0]),
                                      front_size[3] + start_size[3] + bottom_size[1] + 10))

        self.x1 = head_length
        self.x2 = head_length - start_size[2] - 10
        self.x3 = head_length + time_size
        self.y1 = front_size[3] + start_size[3]
        self.y2 = self.y1 - start_size[3] + start_size[1]

    def draw_white(self, draw: ImageDraw.ImageDraw) -> None:
        font = ImageFont.truetype(cjk_font_path, 36)
        draw.text((self.x1, self.y1 - 36), self.front, anchor="rb", font=font)
        draw.text((self.x1, self.y1), self.start, anchor="rb", font=font)

        draw.text((self.x3, self.y1), self.end, anchor="lb", font=font)

        font = ImageFont.truetype(ascii_font_path, 18)
        draw.text((self.x2 + 15, self.y1 + 10), str(self.bottom), font=font)

    def make_shadow(self, pic: Image.Image) -> Image.Image:
        output = Image.new("RGBA", pic.size)
        output.paste(Image.new("RGBA", pic.size, "Black"), mask=pic.convert("LA"))
        output = output.filter(ImageFilter.GaussianBlur(7))
        output.paste(pic, mask=pic)
        return output

    def make_rgb(self, pic: Image.Image) -> Image.Image:
        output = Image.new("RGB", pic.size)
        output.paste(pic, mask=pic)
        return output

    def create_static(self) -> bytes:
        self.create_background()
        draw = ImageDraw.Draw(self.pic)
        self.draw_white(draw)

        font = ImageFont.truetype(ascii_font_path, 90)
        draw.text((self.x1, self.y1), str(self.time), anchor="lb", fill="Red", font=font)


        self.pic = ImageOps.expand(self.pic, border=30)
        output = self.make_shadow(self.pic)

        # Make Red Line
        size = (self.x2 + 30, self.y2 + 30, self.x2 + 34, self.pic.height - 30)
        ImageDraw.Draw(output).rectangle(size, "Red")

        output.save(b := BytesIO(), format="png")

        return b.getvalue()

    def create_animate(self) -> bytes:
        assert isinstance(self.time, int)

        self.create_background()
        draw = ImageDraw.Draw(self.pic)
        self.draw_white(draw)

        font = ImageFont.truetype(ascii_font_path, 90)

        outputs = []
        for i in range(self.time ,-1, -1):
            pic = self.pic.copy()
            pic_draw = ImageDraw.Draw(pic)
            pic_draw.text((self.x1 + self.time_size // 2, self.y1),
                          str(i),
                          anchor="mb",
                          fill="Red",
                          font=font)
            output = ImageOps.expand(pic, border=30)

            output = self.make_shadow(output) if self.rgba else self.make_rgb(output)

            # Make Red Line
            size = (self.x2 + 30, self.y2 + 30, self.x2 + 34, self.pic.height+30)
            ImageDraw.Draw(output).rectangle(size, "Red")

            outputs.append(output)

        outputs[0].save(b := BytesIO(),
                        format="gif",
                        save_all=True,
                        append_images=outputs[1:],
                        duration=1000,
                        transparency=0,
                        disposal=2)

        return b.getvalue()

    def get_pic(self) -> bytes:
        return self.create_animate() if self.gif else self.create_static()


def make_pic(front: str,
             start: str,
             time: int | str,
             end: str,
             bottom: str,
             rgba: bool = True,
             gif: bool = False):
    return CountDownImage(front, start, time, end, bottom, rgba, gif).get_pic()



if __name__ == "__main__":
    c = CountDownImage("距离考试结束", "大约还有", 15, "分钟", "Fxxxing, 15min\nQuickly")
    c.create_animate()
