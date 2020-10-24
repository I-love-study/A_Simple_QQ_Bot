import time
import asyncio
import aiofiles
import aiofiles.os
from PIL import Image as IMG
from io import BytesIO
from graia.application.logger import LoggingLogger

def count_time(name = 'Unknown'):
    def wrapper(func):
        def deco(*args, **kwargs):
            t = time.time()
            result = func(*args, **kwargs)
            LoggingLogger().info(f'{name}用时{round(time.time()-t,2)}s')
            return result
        return deco
    return wrapper

@count_time('图片压制')
def zip_pic(data, size):
    if len(data) < size:
        return data
    img = IMG.open(BytesIO(data))
    img_mode = {'RGBA' : 'PNG', 'RGB' : 'JPEG', 'P' : 'GIF'}
    ext = img_mode[img.mode] if img.mode in img_mode else 'JPEG'
    img_buffer = BytesIO()
    img.save(img_buffer, format = ext, quality = 70)
    while (img_size := len(img_buffer.getvalue())) > size:
        img_buffer = BytesIO()
        rate = (size/img_size)**0.5-0.1
        w, h = img.size
        img = img.resize((int(w*rate), int(h*rate)), IMG.ANTIALIAS)
        img.save(img_buffer, format = ext, quality = 70)
    return img_buffer.getvalue()

@count_time('音频压制')
async def silk(data, mtype = 'b' , options = ''):
    cache_files = ['cache.wav', 'cache.slk']

    if mtype == 'f':
        file = data
    elif mtype == 'b':
        async with aiofiles.open('music_cache', 'wb') as f:
            await f.write(data)
        file = 'music_cache'
        cache_files.append(file)
    else:
        raise ValueError("Not fit music_type. only 'f' and 'b'")

    cmd = [f'ffmpeg -i "{file}" {options} -af aresample=resampler=soxr '\
            '-ar 24000 -ac 1 -y -loglevel error "cache.wav"',
           f'"lib/silk_v3_encoder.exe" cache.wav cache.slk -quiet -tencent']

    for p in cmd:
        shell = await asyncio.create_subprocess_shell(p)
        await shell.wait()

    async with aiofiles.open(f'cache.slk', 'rb') as f:
         b = await f.read()
    #清除cache
    for cache_file in cache_files:
        await aiofiles.os.remove(cache_file)
    return b