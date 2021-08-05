from graia.application import GraiaMiraiApplication
from graia.application.event.messages import GroupMessage
from graia.application.message.elements.internal import *
from graia.application.message.chain import MessageChain
from graia.application.message.parser.kanata import Kanata
from graia.application.message.parser.signature import FullMatch, RequireParam
from graia.application.group import Group, Member
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

from PIL import Image as IMG, ImageDraw, ImageFont
from io import BytesIO
import numpy as np
from decimal import Decimal, ROUND_HALF_UP
from time import time
from math import radians, tan, cos, sin
import shlex

channel = Channel.current()

channel.name("5000M")
channel.description("发送'5000m [词] [词]'制作'5000兆円欲しい'图片")
channel.author("I_love_study")

@channel.use(ListenerSchema(
    listening_events=[GroupMessage],
    inline_dispatchers=[Kanata([FullMatch('5000m'), RequireParam('para')])]
    ))
async def give5000M(app: GraiaMiraiApplication, group: Group, para: MessageChain):
    if len(tag:=shlex.split(para.asDisplay())) == 2:
        pic = BytesIO()
        genImage(*tag).save(pic, format='PNG')
        msg = [Image.fromUnsafeBytes(pic.getvalue())]
    else:
        msg = [Plain('消息有误，请重试')]
    await app.sendGroupMessage(group, MessageChain.create(msg))

_round = lambda f, r=ROUND_HALF_UP: int(Decimal(str(f)).quantize(Decimal("0"), rounding=r))
rgb = lambda r, g, b: (r, g, b)

def getTextWidth(text, font, width=100, height=500, recursive=False):
    step = 100
    img = IMG.new("L", (width, height))
    draw = ImageDraw.Draw(img)
    draw.text((0, 0), text, font=font, fill=255)
    box = img.getbbox()
    if box[2] < width-step or (recursive and box[2] == width-step):
        return box[2]
    else:
        return getTextWidth(text=text, font=font, width=width+step, height=height, recursive=True)

def get_gradient_3d(width, height, start_list, stop_list):
    result = np.zeros((height, width, len(start_list)), dtype=float)
    for i, (start, stop) in enumerate(zip(start_list, stop_list)):
        result[:, :, i] = np.tile(np.linspace(start, stop, height), (width, 1)).T
    return result

def createLinearGradient(steps, width, height):
    result = np.zeros((0, 1, len(steps[0])), dtype=float)
    for i, k in enumerate(steps.keys()):
        if i == 0: continue
        pk = list(steps.keys())[i-1]
        h = _round(height*(k-pk))
        array = get_gradient_3d(1, h, steps[pk], steps[k])
        result = np.vstack([result, array])
    return np.tile(result, (width, 1))

def genBaseImage(width=1500, height=150):
    downerSilverArray = createLinearGradient({
        0.0: rgb(0, 15, 36),
        0.10: rgb(255, 255, 255),
        0.18: rgb(55, 58, 59),
        0.25: rgb(55, 58, 59),
        0.5: rgb(200, 200, 200),
        0.75: rgb(55, 58, 59),
        0.85: rgb(25, 20, 31),
        0.91: rgb(240, 240, 240),
        0.95: rgb(166, 175, 194),
        1: rgb(50, 50, 50)
    }, width=width, height=height)
    goldArray = createLinearGradient({
        0: rgb(253, 241, 0),
        0.25: rgb(245, 253, 187),
        0.4: rgb(255, 255, 255),
        0.75: rgb(253, 219, 9),
        0.9: rgb(127, 53, 0),
        1: rgb(243, 196, 11)
    }, width=width, height=height)
    redArray = createLinearGradient({
        0: rgb(230, 0, 0),
        0.5: rgb(123, 0, 0),
        0.51: rgb(240, 0, 0),
        1: rgb(5, 0, 0)
    }, width=width, height=height)
    strokeRedArray = createLinearGradient({
        0: rgb(255, 100, 0),
        0.5: rgb(123, 0, 0),
        0.51: rgb(240, 0, 0),
        1: rgb(5, 0, 0)
    }, width=width, height=height)
    silver2Array = createLinearGradient({
        0: rgb(245, 246, 248),
        0.15: rgb(255, 255, 255),
        0.35: rgb(195, 213, 220),
        0.5: rgb(160, 190, 201),
        0.51: rgb(160, 190, 201),
        0.52: rgb(196, 215, 222),
        1.0: rgb(255, 255, 255)
    }, width=width, height=height)
    navyArray = createLinearGradient({
        0: rgb(16, 25, 58),
        0.03: rgb(255, 255, 255),
        0.08: rgb(16, 25, 58),
        0.2: rgb(16, 25, 58),
        1: rgb(16, 25, 58)
    }, width=width, height=height)
    result = {
        "downerSilver": IMG.fromarray(np.uint8(downerSilverArray)).crop((0, 0, width, height)),
        "gold": IMG.fromarray(np.uint8(goldArray)).crop((0, 0, width, height)),
        "red": IMG.fromarray(np.uint8(redArray)).crop((0, 0, width, height)),
        "strokeRed": IMG.fromarray(np.uint8(strokeRedArray)).crop((0, 0, width, height)),
        "silver2": IMG.fromarray(np.uint8(silver2Array)).crop((0, 0, width, height)),
        "strokeNavy": IMG.fromarray(np.uint8(navyArray)).crop((0, 0, width, height)),  # Width: 7
        "baseStrokeBlack": IMG.new("RGBA", (width, height), rgb(0, 0, 0)),  # Width: 17
        "strokeBlack": IMG.new("RGBA", (width, height), rgb(16, 25, 58)),  # Width: 17
        "strokeWhite": IMG.new("RGBA", (width, height), rgb(221, 221, 221)),  # Width: 8
        "baseStrokeWhite": IMG.new("RGBA", (width, height), rgb(255, 255, 255))  # Width: 8
    }
    for k in result.keys():
        result[k].putalpha(255)
    return result

def genImage(word_a="5000兆円", word_b="欲しい!", default_width=1500, height=500,
    bg="white", subset=250, default_base=None):
    # width = max_width
    alpha = (0, 0, 0, 0)
    leftmargin = 50
    font_upper = font_downer = ImageFont.truetype(r"src/font/SourceHanSans-Medium.otf", _round(height/3))

    # Prepare Width

    upper_width = max([default_width,
                      getTextWidth(word_a, font_upper, width=default_width,
                                   height=_round(height/2))]) + 300
    downer_width = max([default_width,
                       getTextWidth(word_b, font_downer, width=default_width,
                                    height=_round(height/2))]) + 300


    max_width = max([upper_width, downer_width])
    base = genBaseImage(width=max_width, height=_round(height/2))

    # Prepare base - Upper
    upper_base = base.copy()
    if max_width != upper_width:
        for line in upper_base.keys():
            upper_base[line] = upper_base[line].crop((0, 0, upper_width, _round(height/2)))

    # Prepare base - Downer
    downer_base = base.copy()
    if max_width != downer_width+leftmargin:
        for line in downer_base.keys():
            downer_base[line] = downer_base[line].crop((0, 0, downer_width+leftmargin, _round(height/2)))

    # Prepare & Draw mask - Upper
    img_upper = IMG.new("RGBA", (upper_width, _round(height/2)), alpha)
    upper_data = [
        [
            (4, 4), (4, 4), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)
        ], [
            22, 20, 16, 10, 6, 6, 4, 0
        ], [
            "baseStrokeBlack",
            "downerSilver",
            "baseStrokeBlack",
            "gold",
            "baseStrokeBlack",
            "baseStrokeWhite",
            "strokeRed",
            "red",
        ]
    ]
    for pos, stroke, color in zip(upper_data[0], upper_data[1], upper_data[2]):
        mask_img_upper = IMG.new("L", (upper_width, _round(height/2)), 0)
        ImageDraw.Draw(mask_img_upper).text(
            (pos[0], pos[1]), word_a,
            font=font_upper, fill=255,
            stroke_width=_round(stroke*height/500))
        img_upper.paste(upper_base[color], (0, 0), mask=mask_img_upper)

    # Prepare & Draw mask - Downer
    img_downer = IMG.new("RGBA", (downer_width+leftmargin, _round(height/2)), alpha)
    downer_data = [
        [
            (5, 2), (5, 2), (0, 0), (0, 0), (0, 0), (0, -3)
        ], [
            22, 19, 17, 8, 7, 0
        ], [
            "baseStrokeBlack",
            "downerSilver",
            "strokeBlack",
            "strokeWhite",
            "strokeNavy",
            "silver2"
        ]
    ]
    for pos, stroke, color in zip(downer_data[0], downer_data[1], downer_data[2]):
        mask_img_downer = IMG.new("L", (downer_width+leftmargin, _round(height/2)), 0)
        ImageDraw.Draw(mask_img_downer).text(
            (pos[0]+leftmargin, pos[1]), word_b,
            font=font_downer, fill=255,
            stroke_width=_round(stroke*height/500))
        img_downer.paste(downer_base[color], (0, 0), mask=mask_img_downer)

    # tilt image
    angle = 20
    def tilt(img):
        dist = img.height * tan(radians(angle))
        data = (1, tan(radians(angle)), -dist, 0, 1, 0)
        imgc = img.crop((0, 0, img.width+dist, img.height))
        imgt = imgc.transform(imgc.size, IMG.AFFINE, data, IMG.BILINEAR)
        return imgt

    # finish
    previmg = IMG.new("RGBA", (max([upper_width, downer_width])+leftmargin+300, height), alpha)
    previmg.alpha_composite(tilt(img_upper), (0, 0), (0, 0))
    previmg.alpha_composite(tilt(img_downer), (subset, _round(height/2)), (0, 0))
    croprange = previmg.convert("RGB").getbbox()
    img = previmg.crop(croprange)

    return img

'''
def main():
    t = time()
    #base = genBaseImage(width=width, height=_round(height/2))
    #print("genBaseImage Time :", time()-t)
    i = genImage("5000兆円")
    i.save("5000.png")
    #i.show()
    print("Time :", time()-t)'''