import hashlib
from random import randint
import string
import time
import base64
import aiohttp
from urllib.parse import urlencode

app_id=
app_key=''
tx_headers = {"Content-Type":"application/x-www-form-urlencoded"}

def sign(req_data):#腾讯Ai的sign计算
    new_list = dict(sorted((x, y) for x, y in req_data.items() if y))
    encode_list = urlencode(new_list)
    req_data = encode_list + "&" + "app_key" + "=" + app_key
    md5 = hashlib.md5()
    md5.update(req_data.encode('utf-8'))
    data = md5.hexdigest()
    return data.upper()
def get_nonce_str():#随机字符串
    nonce_str = ''
    len_str = string.digits + string.ascii_letters
    for i in range(len('fa577ce340859f9fe')):
        nonce_str += len_str[randint(0, len(len_str) - 1)]
    return nonce_str
async def ero_pic(data,data_type):#色图识别
    url="https://api.ai.qq.com/fcgi-bin/vision/vision_porn"
    req_data = {
        'app_id': app_id,
        'time_stamp': int(time.time()),
        'nonce_str': get_nonce_str(),
        }
    if data_type == 'url':
        req_data['image_url'] = data
    elif data_type == 'b64_data':
        req_data['image'] = data
    elif data_type == 'data':
        req_data['image'] = base64.b64encode(data).decode('ascii')
    req_data['sign'] = sign(req_data)
    req_data = sorted(req_data.items())
    async with aiohttp.request("POST", url, data=urlencode(req_data), headers=tx_headers)as r:
        return await r.json()
    #return requests.post(url,data=req_data).json()
async def ocr(data, data_type):#OCR识别
    url = "https://api.ai.qq.com/fcgi-bin/ocr/ocr_generalocr"
    req_data = {
        'app_id': app_id,
        'time_stamp': int(time.time()),
        'nonce_str': get_nonce_str(),
        }
    if data_type == 'b64_data':
        req_data['image'] = data
    elif data_type == 'data':
        req_data['image'] = base64.b64encode(data).decode('ascii')
    req_data['sign'] = sign(req_data)
    req_data = sorted(req_data.items())
    async with aiohttp.request("POST", url, data=req_data, headers=tx_headers)as r:
        return await r.json()
async def text(text):#语音说话
    url="https://api.ai.qq.com/fcgi-bin/nlp/nlp_textchat"
    req_data = {
        'app_id': app_id,
        'time_stamp': int(time.time()),
        'nonce_str': get_nonce_str(),
        'session' : randint(100,1000000000),
        'question' : text
        }
    req_data['sign'] = sign(req_data)
    req_data = sorted(req_data.items())
    async with aiohttp.request("POST",url,data=req_data)as r:
        data = await r.json()
        back = data['data']['answer']
        if back != '':
            return back
        else:
            return '？'
async def voice_tts(text):
    while len(text.encode('UTF-8')) > 150:#tx要求文字不多于150字节
        text = text[:-1]#一个一个减，不知道有什么更好的办法了。。
    url = "https://api.ai.qq.com/fcgi-bin/aai/aai_tts"
    req_data = {
        'app_id': app_id,
        'time_stamp': int(time.time()),
        'nonce_str': get_nonce_str(),
        'speaker':7,#碧萱女声
        'format':3,#mp3文件，一切都是为了高速
        'volume':0,
        'speed':100,
        'text':text,
        'aht':8,
        'apc':47.5,
    }
    req_data['sign'] = sign(req_data)
    req_data = sorted(req_data.items())
    tx_headers = {"Content-Type":"application/x-www-form-urlencoded"}
    async with aiohttp.request("POST", url, data=req_data, headers=tx_headers)as r:
        response = await r.json()
    print(response)
    if response['ret'] == 0:
        return response['data']['speech']
