from PIL import Image, ImageFont, ImageDraw
from io import BytesIO
from typing import Literal
from pathlib import Path
from itertools import product

font_path = str(Path("static") / "font" / "SourceHanSans-Medium.otf")
ZH_TOP = "请选择包含"
ZH_BOTTOM = "的所有图块，如果没有，请点击“跳过”"
EN_TOP = "Select all squares with"
EN_BOTTOM = "If there are none, clik skip"


def gen_verification(name: str, image_bytes: bytes, language: Literal["en", "zh"] = "zh") -> bytes:
    image = Image.open(BytesIO(image_bytes))
    image = image.resize((900, 900), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (1000, 1535), "#FFF")
    length = 225
    font_big = ImageFont.truetype(font_path, 70)
    font_small = ImageFont.truetype(font_path, 40)

    for i, j in product(range(4), repeat=2):
        box = (length * i, length * j, length * (i + 1), length * (j + 1))
        canvas.paste(image.crop(box), (19 + i * (233 + 10), 370 + j * (233 + 10)))

    banner = Image.new("RGB", (962, 332), "#4790E4")
    draw = ImageDraw.Draw(banner)
    draw.text((70, 60), ZH_TOP if language == "zh" else EN_TOP, "white", font_small)
    draw.text((70, 120), name, "white", font_big)
    draw.text((70, 230), ZH_BOTTOM if language == "zh" else EN_BOTTOM, "white", font_small)
    canvas.paste(banner, (19, 19))

    bottom = Image.new("RGB", (1000, 182), "#FFF")
    button = Image.new("RGB", (282, 120), "#4790E4")
    draw = ImageDraw.Draw(button)
    draw.text(
        (141, 60),
        ("跳过" if language == "zh" else "SKIP"),
        "white", font_small, anchor="mm"
    )
    bottom.paste(button, (687, 30))
    bottom_border = Image.new("RGB", (1002, 186), "#D5D5D5")
    bottom_border.paste(bottom, (2, 2))
    canvas.paste(bottom_border, (-2, 1353))

    res = Image.new("RGB", (1004, 1539), "#D5D5D5")
    res.paste(canvas, (2, 2))
    res.save(b := BytesIO(), format="jpeg")
    return b.getvalue()