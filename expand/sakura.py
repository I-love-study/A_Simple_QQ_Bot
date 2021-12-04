from typing import Union
from io import BytesIO
from pathlib import Path

from graia.application.message.elements.internal import Plain, At, Image
from graia.application.message.chain import MessageChain
from graia.application.group import Group, Member
from expand.text import EmojiWriter
from expand.data_orm import *

import aiohttp
from PIL import Image as IMG, ImageDraw, ImageFont, ImageFilter, ImageChops

emoji_write = EmojiWriter()

async def user_at_message(member: Union[int, Member], pic: bool = True, r_type = list):
    member_id = member.id if isinstance(member, Member) else member
    member_info = select_member(member_id)
    mes = [Plain(f"「{member_info.get('rank', '无头衔')}」"),
            At(target = member_id)]
    if pic:
        pic_size, avatar_size = 640, 360
        async with aiohttp.request("GET", f'http://q2.qlogo.cn/headimg_dl?dst_uin={member_id}&spec=5') as r:
            avatar = IMG.open(BytesIO(await r.read())).resize((pic_size, pic_size), IMG.ANTIALIAS)
        #背景使用通过高斯滤波模糊的头衔
        bg = avatar.copy().filter(ImageFilter.GaussianBlur(radius=7))
        #使用超采样制作圆形mask防抗锯齿
        mask = IMG.new('L', (avatar_size*3, avatar_size*3), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, avatar_size*3, avatar_size*3), fill = 255)
        mask = mask.resize((avatar_size, avatar_size), IMG.ANTIALIAS)
        paste_point = int((pic_size-avatar_size)/2)
        s_avatar = avatar.resize((avatar_size, avatar_size), IMG.ANTIALIAS)
        bg.paste(s_avatar, (paste_point, paste_point), mask=mask)
        #头像框粘贴
        frame_path = None
        avatar_box = Path('src/avatar_box')
        if member_info.avatar_frame is not None:
            frame_path = avatar_box / f"{member_info.avatar_frame}.png"
        if sp := [avatar_box for avatar_box in avatar_box.iterdir() if avatar_box.stem == str(member_id)]:
            frame_path = sp[0]
        if frame_path is not None:
            x = lambda x: int(x*7/4)
            ab = IMG.open(frame_path).resize(map(x, (avatar_size, avatar_size)), IMG.ANTIALIAS)
            paste_s = int((pic_size-ab.size[0])/2)
            bg.paste(ab, (paste_s, paste_s), mask=ab)
        b = BytesIO()
        bg.save(b, format='PNG')
        mes.insert(0,Image.fromUnsafeBytes(b.getvalue()))
    if r_type is MessageChain:
        return MessageChain.create(mes)
    elif r_type is list:
        return mes

async def get_mask_bg(group: Group, member: Member, add=0, pic_size=640, avatar_size=256):
    member_info = select_member(member)
    params=dict(dst_uin=member.id, spec=5)
    async with aiohttp.request("GET", f'http://q2.qlogo.cn/headimg_dl',params=params) as r:
        avatar = IMG.open(BytesIO(await r.read())).resize((pic_size, pic_size), IMG.ANTIALIAS)
    #背景使用通过高斯滤波模糊的头衔
    bg = avatar.copy().filter(ImageFilter.GaussianBlur(radius=7))
    #使用超采样制作圆形mask防抗锯齿
    mask = IMG.new('L', (avatar_size*3, avatar_size*3), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, avatar_size*3, avatar_size*3), fill = 255)
    mask = mask.resize((avatar_size, avatar_size), IMG.ANTIALIAS)
    #缩小头像并粘贴
    s_avatar = avatar.resize((avatar_size, avatar_size), IMG.ANTIALIAS)
    paste_point = int((pic_size-avatar_size)/2)
    bg.paste(s_avatar, (paste_point, paste_point-int(pic_size/8)), mask=mask)
    #头像框粘贴
    frame_path = None
    avatar_box = Path('src/avatar_box')
    if member_info.avatar_frame is not None:
        frame_path = avatar_box / f"{member_info.avatar_frame}.png"
    if sp := [avatar_box for avatar_box in avatar_box.iterdir() if avatar_box.stem == str(member.id)]:
        frame_path = sp[0]
    if frame_path is not None:
        x = lambda x: int(x*7/4)
        ab = IMG.open(frame_path).resize(map(x, (avatar_size, avatar_size)), IMG.ANTIALIAS)
        paste_s = int((pic_size-ab.size[0])/2)
        bg.paste(ab, (paste_s, paste_s-int(pic_size/8)), mask=ab)
    
    #制作半透明圆角矩形(写字用)
    l, h = 540, 160
    write_bg = IMG.new("RGBA", (l,h), (0,0,0,0))
    color, d = (0,0,0,200), 80
    write_draw = ImageDraw.Draw(write_bg)
    write_draw.ellipse((0,0,d,d),fill=color)
    write_draw.ellipse((l-d,0,l,d),fill=color)
    write_draw.ellipse((0,h-d,d,h),fill=color)
    write_draw.ellipse((l-d,h-d,l,h),fill=color)
    write_draw.rectangle((0,d/2,l,h-d/2),fill=color)
    write_draw.rectangle((d/2,0,l-d/2,h),fill=color)
    #在圆角矩形上写字(名字做特殊处理)
    name = member.name
    if emoji_write.get_size(name, 40)[0] > l:
        dot = emoji_write.get_size('...', 40)[0]
        while emoji_write.get_size(name, 40)[0]+dot > l: name = name[:-1]
        name += '...'
    pic_name = emoji_write.text2pic(name, '#FFFFFF', 40)
    write_bg.paste(pic_name,(int((l-pic_name.size[0])/2),5),mask=pic_name)
    # 计算数据ing
    level, experience = divmod(member_info.experience.get(str(group.id), 0), 300)
    if add == 0:
        bars = [(experience,'#FF8C00')]
        bar_word = str(experience)
        get_level = level
    elif experience + add <= 300:
        bars = [(experience+add, '#FFAA00'),(experience,'#FF8C00')]
        bar_word = f'{experience}+{add}'
        get_level = level
    else:
        bars = [(experience+add-300, '#FFAA00')]
        bar_word = f'+{experience+add-300}'
        get_level = f"{level}+1"
    #写其他文字
    word_ttf  = ImageFont.truetype('src/font/SourceHanSans-Heavy.otf', 40)
    write_draw.text((50,52), f"等级:Lv{get_level}", font=word_ttf)
    #write_draw.text((l/2+50,52), f"经验:{level_info.get('experience', 0)}", font=word_ttf)
    good = member_info.cumulative_love_token.get(str(group.id), {}).get("good", 0)
    write_draw.text((l/2+25, 52), f"上签:{good}次", font=word_ttf)
    #绘制进度条
    bar_color1 = '#FFC800'
    write_draw.ellipse(  (150   ,117,180    ,147), fill=bar_color1)
    write_draw.ellipse(  (l-95  ,117,l-65   ,147), fill=bar_color1)
    write_draw.rectangle((180-15,117,l-95+15,147), fill=bar_color1)
    write_draw.text((50,100), '经验:', font=word_ttf)
    #绘制已知进度条
    for v, c in bars:
        if (p := 150 + int((l-65-150)*(v/300))) >= 180:
            write_draw.ellipse(  (150   ,117,180    ,147), fill=c)
            write_draw.ellipse(  (p-30  ,117,p      ,147), fill=c)
            write_draw.rectangle((180-15,117,p-15   ,147), fill=c)
        else:
            dot_bg = IMG.new("RGB", (30,30), (0,0,0,0))
            dot_draw = ImageDraw.Draw(dot_bg)
            dot_draw.ellipse((p-180,0,p-150,30), fill=c)
            ex_bg = IMG.new("1", (30,30), 0)
            ex_draw = ImageDraw.Draw(ex_bg)
            ex_draw.ellipse((0,0,30,30), fill=1)
            mask = ImageChops.darker(dot_bg.convert('1'), ex_bg)
            write_bg.paste(dot_bg, (150,117), mask=mask)

    small_font_ttf = ImageFont.truetype('src/font/SourceHanSans-Heavy.otf', 25)
    num_pixels = small_font_ttf.getsize(bar_word)[0]
    write_draw.text((150+int((l-65-150-num_pixels)/2),113), bar_word,
        font=small_font_ttf)
    #write_draw.text((50, 100), f"共获取上上签:{100}次", font=word_ttf)
    #保存图片
    bg.paste(write_bg, 
        (int((pic_size-l)/2), int(pic_size/2 + avatar_size/2 + 10)),
        mask = write_bg)
    
    # JPEG生产速度比PNG快
    b = BytesIO()
    bg.save(b, format='JPEG', quality=99)
    return b.getvalue()

'''
def change_rank(member_id: int, new_rank: str) -> None:
    if str(member_id) not in rank_data:
        raise ValueError('no data in people')
    if new_rank not in rank_data[str(member_id)]['rank']:
        raise ValueError("you don't have this rank")
    rank_data[str(member_id)]['wear_rank'] = new_rank
    rank_update()
'''