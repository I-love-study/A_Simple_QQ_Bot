from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
import json
import re
from pathlib import Path
from typing import Annotated, Literal

import aiohttp
import PIL.Image
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import App, Image
from graia.ariadne.message.parser.twilight import (ElementMatch, ElementResult,
                                                   RegexMatch, RegexResult,
                                                   ResultValue, Twilight)
from graia.ariadne.model import Group
from graia.saya import Channel
from graiax.shortcut.saya import dispatch, listen
from PIL import ImageFont
from PIL.ImageDraw import Draw

from utils.text import text2pic
from utils.bilibili import get_avatar
import qrcode
import qrcode.constants
from qrcode.image.pil import PilImage

channel = Channel.current()

channel.name("AVBVAU")
channel.description("发送任意av/BV号获取视频信息")
channel.author("I_love_study")

font_path = Path(r"static\font\SourceHanSans-Medium.otf")
font_heavy_path = Path(r"static\font\SourceHanSans-Heavy.otf")
iconfont_path = Path(r"static\font\bilibili-iconfont.ttf")
static_path = Path(__file__).parent / "static"

avid_re = r"(av|AV)(\d{1,12})"
bvid_re = "[Bb][Vv]1([0-9a-zA-Z]{2})4[1y]1[0-9a-zA-Z]7([0-9a-zA-Z]{2})"
b23_re = r"(https?://)?b23.tv/\w+"
url_re = r"(https?://)?www.bilibili.com/video/.+(\?[\w\W]+)?"
p = re.compile(f"({avid_re})|({bvid_re})")
headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) ' \
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}


@listen(GroupMessage)
@dispatch(
    Twilight(
        RegexMatch(avid_re, optional=True) @ "av",
        RegexMatch(bvid_re, optional=True) @ "bv",
        RegexMatch(b23_re, optional=True) @ "b23url",
        RegexMatch(url_re, optional=True) @ "url",
        ElementMatch(App, optional=True) @ "bapp"))
async def video_info(app: Ariadne, group: Group, message: MessageChain, av: RegexResult,
                     bv: RegexResult, b23url: RegexResult, url: RegexResult, bapp: ElementResult):
    if av.matched or bv.matched:
        vid = str(message)
    elif b23url.matched or bapp.matched:
        if bapp.matched:
            app_dict = bapp.result.dict() # type: ignore
            content = json.loads(app_dict.get("content", {}))
            content = content.get("meta", {}).get("detail_1", {})
            print(content)
            if content.get("title") == "哔哩哔哩":
                b23url_str = content.get("qqdocurl")
            else:
                content = json.loads(app_dict.get("content", {}))
                content = content.get("meta", {}).get("news", {})
                print(content)
                if "哔哩哔哩" in content.get("desc", ""):
                    b23url_str = content.get("jumpUrl")
                else:
                    return
        else:
            b23url_str = str(message)
        if not (msg_str := await b23_url_extract(b23url_str)):
            return
        vid = p.search(msg_str).group() # type: ignore
    elif url.matched:
        if not (vid := url_vid_extract(str(message))):
            return
    else:
        return

    async with aiohttp.ClientSession() as session:

        if vid[:2].upper() == "AV":
            param = {"aid": vid[2:]}
        elif vid[:2].upper() == "BV":
            param = {"bvid": vid}
        else:
            raise ValueError("视频 ID 格式错误，只可为 av 或 BV")

        async with session.get(f"https://api.bilibili.com/x/web-interface/view", params=param) as resp:
            video_info = await resp.json(content_type=resp.content_type)

    if video_info['code'] == -404:
        return await app.send_message(group, MessageChain("视频不存在"))
    elif video_info['code'] != 0:
        error_text = f'解析B站视频 {vid} 时出错👇\n错误代码：{video_info["code"]}\n错误信息：{video_info["message"]}'
        return await app.send_message(group, MessageChain(error_text))

    video_info = info_json_dump(video_info["data"])
    pic = PIL.Image.new("RGBA", (960, 1220), (10, 10, 10))
    pic_draw = Draw(pic)
    pic_draw.rectangle((0, 1000, 960, 1220), (20, 20, 20))

    logo = PIL.Image.open(static_path / "bilibili_logo.png").convert(
        "RGBA").resize((240, 120), PIL.Image.LANCZOS)
    pic.paste(logo, (0, 20), mask=logo)

    font = ImageFont.truetype(str(font_path), size=30)
    pic_draw.text((225, 60), "你感兴趣的（二次元）视频都在B站", font=font)

    # buttom_background
    iconfont = ImageFont.truetype(str(iconfont_path), 60)
    background = PIL.Image.new("RGB", (1000, 800), (10, 10, 10))
    back_text = (
        "\ue6e3 \ue6e4 \ue6e1 \ue70f \ue6e3 \ue6e4 \ue6e1 \ue70f \ue6e3 \ue6e4\n "
        "\ue6e1 \ue70f \ue6e3 \ue6e4 \ue6e1 \ue70f \ue6e3 \ue6e4 \ue6e1 \ue70f\n"
    )*3
    Draw(background).multiline_text((0, 0), back_text, font=iconfont, fill=(20, 20, 20), spacing=40)
    background = background.rotate(10, PIL.Image.BICUBIC,expand=True)

    gradient = PIL.Image.linear_gradient("L").resize((background.width, 100), PIL.Image.LANCZOS)
    background_mask = PIL.Image.new("L", background.size)
    background_mask.paste(gradient, (0, 150))
    background_mask.paste(gradient.rotate(180), (0, 500))
    Draw(background_mask).rectangle((0, 250, background.width, 500), 255)
    pic.paste(background, (-70, 0), mask=background_mask)

    # cover
    async with aiohttp.request("GET", video_info.cover_url, headers=headers) as r:
        cover = PIL.Image.open(BytesIO(await r.read())).resize((720, 450), PIL.Image.LANCZOS)
    cover_mask = PIL.Image.new("L", (1440, 900))
    Draw(cover_mask).rounded_rectangle((0, 0, 1440, 900), 60, 255)
    pic.paste(cover, (120, 200), cover_mask.resize((720, 450), PIL.Image.LANCZOS))

    #play_buttom
    play = PIL.Image.open(static_path / "play_buttom.png").resize(
        (100, 100), PIL.Image.LANCZOS
    ).convert("RGBA")
    pic.paste(play, box=(430, 375), mask=play)

    # Title
    title = text2pic(
        video_info.title, size=40, ret_type="PIL", width=720, height=1,
        word_font_path=str(font_heavy_path)
        )
    pic.paste(title, (120, 690), mask=title)

    # tag
    detail_msg = text2pic(
        f"{analyse_num(video_info.views)} \ue6e3 "
        f"{analyse_num(video_info.likes)} \ue6e0 "
        f"{analyse_num(video_info.coins)} \ue6e4 "
        f"{analyse_num(video_info.danmu)} \ue6e7",
        size=25,
        ret_type="PIL",
        emoji_font_path=str(iconfont_path))
    pic.paste(detail_msg, (120, 750), mask=detail_msg)

    # content
    content = text2pic(video_info.desc,
                       size=20,
                       ret_type="PIL",
                       width=720,
                       height=5,
                       stroke_width=7,
                       color=(200, 200, 200))
    pic.paste(content, (120, 800), content)

    # Publish time
    font = ImageFont.truetype(str(font_path), size=25)
    pic_draw.text((580, 750),
                  f"发布于{str(datetime.fromtimestamp(float(video_info.pub_timestamp)))}",
                  font=font,
                  align="right")

    # avatar
    avatar = await get_avatar(video_info.up_mid, a=150)
    pic.paste(avatar, (50, 1030), avatar)

    # user name
    username = text2pic(video_info.up_name, size=30, width=500, height=1, ret_type="PIL")
    pic.paste(username, (210, 1070), username)

    # fans count(didn't have it)
    #font = ImageFont.truetype(str(font_path), size=25)
    #pic_draw.text((210, 1110), "57.4万粉丝", font=font)

    # QR Code
    qr = qrcode.QRCode(version=3,
                       error_correction=qrcode.constants.ERROR_CORRECT_L,
                       box_size=10,
                       border=1)
    qr.add_data("https://bilibili.com/video/" + vid)
    qr.make(fit=True)
    qrimg = qr.make_image(fill_color=(229, 229, 229), back_color=(20, 20, 20))
    assert isinstance(qrimg, PilImage)
    qrimg = qrimg.resize((130, 130), PIL.Image.LANCZOS).convert("RGBA")
    pic.paste(qrimg, (725, 1055), qrimg)
    qr_round = PIL.Image.open(static_path / "qr_round.png").resize(
        (180, 207), PIL.Image.LANCZOS).convert("RGBA")
    pic.paste(qr_round, (700, 1005), qr_round)

    #QR
    font = ImageFont.truetype(str(font_path), size=25)
    pic_draw.text((550, 1080), "扫描二维码\n进入详细页", font=font, align="right")

    pic.convert("RGB").save(b := BytesIO(), format="jpeg", quality=99)
    await app.send_message(group, MessageChain(
        Image(data_bytes=b.getvalue())
    ))



async def b23_url_extract(b23_url: str) -> Literal[False] | str:
    url = re.search(r'b23.tv[/\\]+([0-9a-zA-Z]+)', b23_url)
    if url is None:
        return False
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://{url.group()}', allow_redirects=True) as resp:
            target = str(resp.url)
    return target if 'www.bilibili.com/video/' in target else False

def url_vid_extract(url: str) -> Literal[False] | str:
    try:
        return url.split("?")[0].strip("/").split("/")[-1]
    except IndexError:
        return False

@dataclass
class VideoInfo:
    cover_url: str  # 封面地址
    bvid: str  # BV号
    avid: int  # av号
    title: str  # 视频标题
    sub_count: int  # 视频分P数
    pub_timestamp: int  # 视频发布时间（时间戳）
    unload_timestamp: int  # 视频上传时间（时间戳，不一定准确）
    desc: str  # 视频简介
    duration: int  # 视频长度（单位：秒）
    up_mid: int  # up主mid
    up_name: str  # up主名称
    views: int  # 播放量
    danmu: int  # 弹幕数
    likes: int  # 点赞数
    coins: int  # 投币数
    favorites: int  # 收藏量


def info_json_dump(obj: dict) -> VideoInfo:
    return VideoInfo(
        cover_url=obj['pic'],
        bvid=obj['bvid'],
        avid=obj['aid'],
        title=obj['title'],
        sub_count=obj['videos'],
        pub_timestamp=obj['pubdate'],
        unload_timestamp=obj['ctime'],
        desc=obj['desc'].strip(),
        duration=obj['duration'],
        up_mid=obj['owner']['mid'],
        up_name=obj['owner']['name'],
        views=obj['stat']['view'],
        danmu=obj['stat']['danmaku'],
        likes=obj['stat']['like'],
        coins=obj['stat']['coin'],
        favorites=obj['stat']['favorite'],
    )

def analyse_num(num):
    def strofsize(num, level):
        if level >= 2:
            return num, level
        elif num >= 10000:
            num /= 10000
            level += 1
            return strofsize(num, level)
        else:
            return num, level
    units = ['', '万', '亿']
    num, level = strofsize(num, 0)
    if level > len(units):
        level -= 1
    return '{}{}'.format(round(num, 1), units[level])