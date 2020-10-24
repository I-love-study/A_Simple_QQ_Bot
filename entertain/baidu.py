from graia.broadcast.builtin.decoraters import Depend
from graia.application import GraiaMiraiApplication
from graia.application.event.messages import GroupMessage
from graia.application.message.elements.internal import Plain, At, Image
from graia.application.message.chain import MessageChain
from graia.application.message.parser.kanata import Kanata
from graia.application.message.parser.signature import FullMatch, RequireParam
from graia.application.group import Group, Member
from graia.template import Template
from expand import judge
from core import get
import aiohttp, time, urllib
from lxml import etree
import base64

__plugin_name__ = '百度system'
__plugin_usage__ = '"百科 [参数]" 和 "热点"'

headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                       'Chrome/81.0.4044.69 Safari/537.36 Edg/81.0.416.34'}

bcc = get.bcc()
@bcc.receiver(GroupMessage, headless_decoraters = [Depend(judge.active_check_message)],
                            dispatchers = [Kanata([FullMatch('百科'), RequireParam(name = 'tag')])])
async def bdbk(app: GraiaMiraiApplication, group: Group, message: MessageChain, member: Member, tag: MessageChain):
    tags = tag.asDisplay().strip().split(' ',1)
    print(tags)
    bdurl = f'https://baike.baidu.com/item/{urllib.parse.quote(tags[0])}?force=1'
    async with aiohttp.request("GET",bdurl,headers = headers,allow_redirects=True) as r:
        if str(r.url) == 'https://baike.baidu.com/error.html':
            await session.send('sorry,百科并没有相关信息')
            return
        reponse = await r.text()
    page=etree.HTML(reponse)
    if page.xpath('//div[@class="lemmaWgt-subLemmaListTitle"]//text()') != []:
        print('yes')
        if len(tags) == 1:
            catalog = page.xpath('//div[@class="para" and @label-module="para"]/a/text()')
            catalog = [f"{n+1}.{catalog[n].replace(f'{tags[0]}：','')}" for n in range(len(catalog))]
            await app.sendGroupMessage(group, Template("请输入代号\ne.g:/百科 词语 1\n\n"+'\n'.join(catalog)).render())
            return
        use = int(tags[1]) - 1
        path = page.xpath('//div[@class="para" and @label-module="para"]/a/@href')[use]
        bdurl = r'https://baike.baidu.com' + path
        async with aiohttp.request("GET",bdurl,headers = headers) as r:
            reponse = await r.text()
        page = etree.HTML(reponse)
    for i in page.xpath('//div[@class="lemma-summary"]/div//sup'):
        i.getparent().remove(i)
    mem = page.xpath('//div[@class="lemma-summary"]/div//text()')
    print(mem)
    mem = "".join(mem).replace('\n', '').replace('\xa0', '')
    img_url = page.xpath('//div[@class="summary-pic"]/a/img/@src')
    if img_url != []:
        async with aiohttp.request("GET",img_url[0],headers = headers) as r:
            img = await r.read()
        img = Image.fromUnsafeBytes(img)
    else:
        img = Plain('')
    if mem != '':
        await app.sendGroupMessage(group, Template(mem + '\n' + bdurl.replace("?force=1","") + '$img').render(img = img))
    else:
        await app.sendGroupMessage(group, Template('没有简介desu\n'+bdurl.replace("?force=1","")).render())

@bcc.receiver(GroupMessage, headless_decoraters = [Depend(judge.active_check_message)],
                            dispatchers = [Kanata([FullMatch('热点')])])
async def bdbk(app: GraiaMiraiApplication, group: Group, message: MessageChain, member: Member):
    url="http://top.baidu.com/buzz?b=1&fr=topindex"
    async with aiohttp.request("GET",url,headers = headers) as r:
        reponse = await r.text(encoding = 'gb2312')
    html=etree.HTML(reponse)
    get=html.xpath('//a[@class="list-title"]/text()')
    for a in range(0,20):
        get[a]=str(a+1)+"."+get[a]
    await app.sendGroupMessage(group, Template('\n'.join(get[0:10])).render())
