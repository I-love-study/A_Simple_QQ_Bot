import aiohttp, aiofiles
import ujson as json
from Crypto.Cipher import AES
import tqdm, base64, binascii
import os

headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip,deflate,sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8,gl;q=0.6,zh-TW;q=0.4',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Host': 'music.163.com',
    'Referer': 'http://music.163.com/search/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) ' \
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'

}

download_headers={
    'Accept-Encoding': 'identity;q=1, *;q=0',
    'DNT': '1',
    'Range': 'bytes=0-',
    'Referer': 'http://music.163.com/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) ' \
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
}

async def post_requests(url, params):
    data = encrypyed().encrypted_request(params)
    async with aiohttp.request("POST", url, data = data, headers = headers) as r:
        result = await r.read()
        return json.loads(result)

async def search(search_content,search_type=1, limit=9):
    url = r'http://music.163.com/weapi/cloudsearch/get/web'
    params = {'s': search_content, 'type': search_type, 'offset': 0, 'sub': 'false', 'limit': limit}
    result = await post_requests(url, params)
    result = result['result']['songs']
    return result

async def download_song(song_id):
    url=r'http://music.163.com/weapi/song/enhance/player/url'
    params = {'ids': [song_id], 'br': '128000', 'csrf_token': ''}
    result = await post_requests(url, params)
    download_url = result['data'][0]['url']
    async with aiohttp.request("GET", download_url, headers = download_headers)as r:
        return await r.read()

async def get_song_detail(song_id):
    url = r'http://music.163.com/weapi/v3/song/detail'
    params = {'c':str([{'id':song_id}]),'ids':[song_id],'csrf_token':''}
    result = await post_requests(url, params)
    return result['songs'][0]

class encrypyed():
    """
    解密算法
    """
    def __init__(self):
        self.modulus = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b' \
            '725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda' \
            '92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3' \
            'e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
        self.nonce = '0CoJUm6Qyw8W8jud'
        self.pub_key = '010001'

    # 登录加密算法, 基于https://github.com/stkevintan/nw_musicbox脚本实现
    def encrypted_request(self, text):
        text = json.dumps(text)
        sec_key = self.create_secret_key(16)
        enc_text = self.aes_encrypt(self.aes_encrypt(text, self.nonce), sec_key.decode('utf-8'))
        enc_sec_key = self.rsa_encrpt(sec_key, self.pub_key, self.modulus)
        data = {'params': enc_text, 'encSecKey': enc_sec_key}
        return data

    def aes_encrypt(self, text, secKey):
        pad = 16 - len(text) % 16
        text = text + chr(pad) * pad
        encryptor = AES.new(secKey.encode('utf-8'), AES.MODE_CBC, b'0102030405060708')
        ciphertext = encryptor.encrypt(text.encode('utf-8'))
        ciphertext = base64.b64encode(ciphertext).decode('utf-8')
        return ciphertext

    def rsa_encrpt(self, text, pubKey, modulus):
        text = text[::-1]
        rs = pow(int(binascii.hexlify(text), 16), int(pubKey, 16), int(modulus, 16))
        return format(rs, 'x').zfill(256)

    def create_secret_key(self, size):
        return binascii.hexlify(os.urandom(size))[:16]


async def app_card(song_id):
    data = await get_song_detail(song_id)
    song_name = data['name']
    song_author = '/'.join([ar['name'] for ar in data['ar']])
    song_picture = data['al']['picUrl'].replace('p1.music.126.net', 'p4.music.126.net')
    content = {'app': 'com.tencent.structmsg',
               'desc': '音乐',
               'meta': {'music': {'action': '',
                                  'android_pkg_name': '',
                                  'app_type': 1,
                                  'appid': 100495085,
                                  'desc': song_author,
                                  'jumpUrl': f'https://y.music.163.com/m/song/{song_id}',
                                  'musicUrl': f'http://music.163.com/song/media/outer/url?id={song_id}',
                                  'preview': song_picture,
                                  'sourceMsgId': '0',
                                  'source_icon': '',
                                  'source_url': '',
                                  'tag': '网易云音乐',
                                  'title': song_name}},
               'prompt': f'[分享]{song_name}',
               'ver': '0.0.0.1',
               'view': 'music'}
    #content=f'''{{"app":"com.tencent.structmsg","desc":"音乐","view":"music","ver":"0.0.0.1","prompt":"[分享]{song_name}","meta":{{"music":{{"action":"","android_pkg_name":"","app_type":1,"appid":100495085,"desc":"{song_author}","jumpUrl":"https://y.music.163.com/m/song/{song_id}","musicUrl":"http://music.163.com/song/media/outer/url?id={song_id}","preview":"{song_picture}","sourceMsgId":"0","source_icon":"","source_url":"","tag":"网易云音乐","title":"{song_name}"}}}}}}'''
    return json.dumps(content)