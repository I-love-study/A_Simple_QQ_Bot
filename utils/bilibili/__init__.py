from io import BytesIO
from pathlib import Path

import aiohttp
from PIL import Image, ImageDraw

headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) ' \
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}

static = Path(__file__).parent / "static"

async def get_pic(url):
    async with aiohttp.request("GET", url) as r:
        return Image.open(BytesIO(await r.read()))


async def get_avatar(uid, a=525):
    params = {"mid": uid}
    url = "https://api.bilibili.com/x/space/acc/info"
    async with aiohttp.request("GET", url, params=params) as r:
        info = await r.json()
    img = Image.new("RGBA", (a, a), (0, 0, 0, 0))

    # 粘贴头像
    face_a = int(a / 7 * 4)
    face = (await get_pic(info['face'])).resize((face_a, face_a), Image.Resampling.LANCZOS)
    face_mask = Image.new("L", (face_a * 3, face_a * 3), 0)
    ImageDraw.Draw(face_mask).ellipse((0, 0, face_a * 3, face_a * 3), 255)
    face_mask = face_mask.resize((face_a, face_a), Image.Resampling.LANCZOS)
    paste_point = int((a - face_a) / 2)
    img.paste(face, (paste_point, paste_point), mask=face_mask)

    # 粘贴头像框
    pendant = (await get_pic(info['pendant']['image_enhance'])).resize((a, a),
                                                                       Image.Resampling.LANCZOS)
    img.paste(pendant, (0, 0), mask=pendant)

    # 粘贴小闪电
    def flash(p):
        official_a = int(face_a * 0.3)
        official = Image.open(p).convert("RGBA").resize((official_a, official_a),
                                                        Image.Resampling.LANCZOS)
        off_point = int(a / 2 + face_a / 2**0.5 / 2 - official_a / 2)
        img.paste(official, (off_point, off_point), mask=official)

    if info['official']['role'] in [1, 2, 7]:
        flash(static / "flash_yellow.png")
    elif info['official']['role'] in [3, 4, 5, 6]:
        flash(static / "flash_blue.png")

    return img


async def get_dynamic(uid: int):
    st_url = r"https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history"
    params = {"host_uid": uid, "need_top": 0}

    async with aiohttp.ClientSession() as session:
        while True:
            async with session.get(st_url, headers=headers, params=params) as r:
                resp = await r.json()
                cards = resp['data']['cards']

            #yield from <expr> 表达式如果在异步生成器函数中使用会引发语法错误
            for card in cards:
                yield card

            if resp['data']['has_more'] == 0:
                return
            else:
                params['offset_dynamic_id'] = resp['data']['next_offset']