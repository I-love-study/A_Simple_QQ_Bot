from typing import Annotated, Any, List
import urllib.parse

import aiohttp
import ujson as json
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image
from graia.ariadne.message.parser.twilight import (FullMatch, ResultValue,
                                                   SpacePolicy, Twilight,
                                                   WildcardMatch, RegexMatch)
from graia.ariadne.model import Group
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from lxml import etree

headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                       'Chrome/81.0.4044.69 Safari/537.36 Edg/81.0.416.34'}

channel = Channel.current()

channel.name("BaiduSearch")
channel.description("发送'百科 [词语]'获取拜读百科词条\n发送热点获取百度热点Top10")
channel.author("I_love_study")

@channel.use(ListenerSchema(
    listening_events=[GroupMessage],
    inline_dispatchers=[Twilight(
        FullMatch("百科").space(SpacePolicy.FORCE),
        WildcardMatch() @ "para"
    )]
))
async def bdbk(app: Ariadne, group: Group, para: Annotated[MessageChain, ResultValue()]):
    tags = str(para).strip().split(' ',1)

    bdurl = f'https://baike.baidu.com/item/{urllib.parse.quote(tags[0])}?force=1'
    async with aiohttp.request("GET", bdurl, headers = headers, allow_redirects = True) as r:
        if str(r.url).startswith('https://baike.baidu.com/error.html'):
            return await app.send_group_message(group, MessageChain('sorry,百科并没有相关信息'))
        reponse = await r.text()

    page = etree.HTML(reponse) #type: ignore
    if page.xpath('//div[@class="lemmaWgt-subLemmaListTitle"]//text()') != []:
        if len(tags) == 1:
            catalog = page.xpath('//div[@class="para" and @label-module="para"]/a/text()')
            await app.send_group_message(group, MessageChain(
                f"请输入代号\ne.g:百科 {tags[0]} 1\n\n",
                '\n'.join(f"{n}.{w.replace(f'{tags[0]}：','')}" for n, w in enumerate(catalog, 1))
                ))
            return
        use = int(tags[1]) - 1
        path = page.xpath('//div[@class="para" and @label-module="para"]/a/@href')[use]
        bdurl = f'https://baike.baidu.com{path}'
        async with aiohttp.request("GET",bdurl,headers = headers) as r:
            reponse = await r.text()
        page = etree.HTML(reponse) #type: ignore

    for i in page.xpath('//div[@class="lemma-summary"]/div//sup'):
        i.getparent().remove(i)

    mem = page.xpath('//div[@class="lemma-summary"]/div//text()')
    mem = "".join(mem).replace('\n', '').replace('\xa0', '')

    msg: List[Any] = [f"{mem or '没有简介desu'}\n{bdurl.replace('?force=1','')}"]

    if (img_url := page.xpath('//div[@class="summary-pic"]/a/img/@src')):
        msg.append(Image(url=img_url[0]))

    await app.send_group_message(group, MessageChain(msg))

@channel.use(ListenerSchema(
    listening_events=[GroupMessage],
    inline_dispatchers=[Twilight([FullMatch("热点"), RegexMatch("[0-9]*") @ "para"])]
))
async def bdrd(app: Ariadne, group: Group, para: Annotated[MessageChain, ResultValue()]):
    url = "https://top.baidu.com/board?tab=realtime"
    async with aiohttp.request("GET", url, headers=headers) as r:
        reponse = await r.text()
    html = etree.HTML(reponse) #type: ignore
    get = json.loads(
        html.xpath("//div[@theme='realtime']/comment()")[0].text[7:]
    )['data']['cards'][0]['content']
    if para:
        get = get[int(str(para)) - 1]
        await app.send_group_message(group, MessageChain(f"{get['word']}:\n{get['desc']}"))
    else:
        get_list = [f"{n}.{p['word']}" for n, p in enumerate(get, 1)]
        await app.send_group_message(group, MessageChain('\n'.join(get_list[:10])))