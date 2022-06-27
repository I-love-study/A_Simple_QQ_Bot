from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import *
from graia.ariadne.message.parser.twilight import Twilight, RegexMatch, WildcardMatch, MatchResult
from graia.ariadne.model import Group, Member
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

from io import BytesIO
from pathlib import Path

from PIL import Image as IMG, ImageDraw, ImageFont
import qrcode
import aiohttp

from expand.text import analyse_font
from expand import bilibili

channel = Channel.current()

channel.name("biliAU号")
channel.description("发送任意AU号获取信息")
channel.author("I_love_study")

@channel.use(ListenerSchema(
    listening_events=[GroupMessage],
    inline_dispatchers=[Twilight(
        [RegexMatch("AU|au"), WildcardMatch() @ "para"]
    )]
))
async def audio_info(app: Ariadne, group: Group, para: MatchResult):
    if not (t := para.result.display).isdigit():
        return

    await app.send_group_message(group, MessageChain([
        Image(data_bytes=await audio_make(int(t)))
    ]))

async def audio_make(auid):
    url = "https://www.bilibili.com/audio/music-service-c/web/song/info"
    params = {"sid": auid}
    async with aiohttp.request("GET", url, params=params) as r:
        data = await r.json()

    qr = qrcode.QRCode(
        version=3,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10, border = 1
    )
    qr.add_data(f"https://www.bilibili.com/audio/au{auid}")
    qr.make(fit=True)
    '''因为太耗时了所以删了
    qrimg = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer(),
        color_mask=SolidFillColorMask(front_color=(229,229,229),back_color=(26,26,26))
         )
    '''
    src_path = Path(__file__).parent / "src"

    qrimg = qr.make_image(fill_color=(229,229,229),back_color=(26,26,26))
    qrimg = qrimg.resize((165, 162), IMG.ANTIALIAS)
    bottom = IMG.open(src_path/"black_down.png")
    qrimg_mask = IMG.new("1", (165, 162))
    ImageDraw.Draw(qrimg_mask).rounded_rectangle([0, 0, 165, 162], 6, 1)
    bottom.paste(qrimg, (654, 75), mask=qrimg_mask)
    
    async with aiohttp.request("GET", data["cover"]) as r:
        cover = await r.read()
    music_img = IMG.open(BytesIO(cover)).resize((280, 280))
    music_mask = IMG.new("1", (280, 280))
    ImageDraw.Draw(music_mask).rounded_rectangle([0, 0, 280, 280], 10, 1)
    music_bg = IMG.open(src_path/"audio_pic_bg.png").convert("RGBA")
    music_bg.paste(music_img, (8, 30), mask=music_mask)
    
    bg = IMG.new("RGBA", (1080, 900), (26, 26, 26))
    bgd = ImageDraw.Draw(bg)
    bg.paste(bottom, (0, 602))
    bg.alpha_composite(music_bg, (100, 230))

    font = ImageFont.truetype(r"src/font/SourceHanSansHW-Bold.otf", size=60)
    l = (1080-font.getsize(data["title"])[0])/2
    if l < 0:
        n = 1080-font.getlength("...")
        while font.getlength(data["title"]) > n:
            data["title"] = data["title"][:-1]
        data["title"] += "..."
        l = (1080-font.getsize(data["title"])[0])/2
    bgd.text((l, 75), data["title"], font=font, fill=(229, 229, 229))

    '''
    user = (await User(data["uid"]).get_user_info())["face"]
    async with aiohttp.request("GET", user) as r:
        face = await r.read()
    avatar = IMG.open(BytesIO(face)).resize((100, 100)).convert("RGBA")
    avatar_mask = IMG.new("1", (300, 300))
    ImageDraw.Draw(avatar_mask).ellipse((0, 0, 300, 300), 1)
    bg.paste(avatar, (450, 225), mask=avatar_mask.resize((100, 100)))
    '''

    avatar = await bilibili.get_avatar(data["uid"], a=180)
    bg.alpha_composite(avatar, (420, 185))

    font = ImageFont.truetype(r"src/font/SourceHanSansHW-Bold.otf", size=40)
    bgd.text((600, 240), data["uname"], fill=(229, 229, 229), font=font)

    icon_font = ImageFont.truetype(r"src/font/bilibili-iconfont.ttf", size=45)
    bgd.multiline_text((420, 370), "\ue6e3\n\n\ue6e4\n\n\ue6e1", 
             fill=(229, 229, 229), font=icon_font)
    font = ImageFont.truetype(r"src/font/SourceHanSansHW-Bold.otf", size=34)

    bgd.text(
        (470, 365),
        (f"{analyse_num(data['statistic']['play'])}\n\n"
         f"{analyse_num(data['coin_num'])}\n\n"
         f"{analyse_num(data['statistic']['collect'])}"),
        fill=(229, 229, 229), font=font)
    
    font = ImageFont.truetype(r"src/font/SourceHanSansHW-Bold.otf", size=25)
    ana = analyse_font(400, data['intro'], font)
    if len(a := ana.split("\n")) >= 8:
        ana = "\n".join([*a[:7], "..."])
    bgd.text((600, 350), f"简介\n{ana}",
            fill=(229, 229, 229), font=font)
    
    #转换为RGB和降低compress_level都是为了加速导出速度 
    bg.convert("RGB").save(b := BytesIO(), format="png", compress_level=1)
    return b.getvalue()
    

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