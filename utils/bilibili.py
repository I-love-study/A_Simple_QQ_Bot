from io import BytesIO

import aiohttp
from bilibili_api import user
from PIL import Image, ImageDraw, ImageFont

async def get_pic(url):
    async with aiohttp.request("GET", url) as r:
        return Image.open(BytesIO(await r.read()))

async def get_avatar(uid, a=525, full_ver=False):
    info = await user.User(uid).get_user_info()
    img = Image.new("RGBA", (a,a), (0,0,0,0))

    # 粘贴头像
    face_a = int(a/7*4)
    face = (await get_pic(info['face'])).resize((face_a, face_a), Image.ANTIALIAS)
    face_mask = Image.new("L", (face_a*3,face_a*3), 0)
    ImageDraw.Draw(face_mask).ellipse((0,0,face_a*3,face_a*3), 255)
    face_mask = face_mask.resize((face_a, face_a), Image.ANTIALIAS)
    paste_point = int((a-face_a)/2)
    img.paste(face, (paste_point, paste_point), mask=face_mask)

    # 粘贴头像框
    pendant = (await get_pic(info['pendant']['image_enhance'])).resize((a,a), Image.ANTIALIAS)
    img.paste(pendant, (0,0), mask=pendant)

    # 粘贴小闪电
    def flash(p):
        official_a = int(face_a*0.3)
        official = Image.open(p).convert("RGBA", palette=Image.ANTIALIAS)\
                                .resize((official_a, official_a), Image.ANTIALIAS)
        off_point = int(a/2+face_a/2**0.5/2-official_a/2)
        img.paste(official, (off_point, off_point), mask=official)

    if info['official']['role'] in [1, 2, 7]:
        flash(r"utils/bilibili_src/flash_yellow.png")
    elif info['official']['role'] in [3, 4, 5, 6]:
        flash(r"utils/bilibili_src/flash_blue.png")
    
    return img