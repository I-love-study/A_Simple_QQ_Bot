from graia.broadcast.builtin.decoraters import Depend
from graia.application import GraiaMiraiApplication
from graia.application.event.messages import GroupMessage
from graia.application.message.elements.internal import Plain, At, Image
from graia.application.message.chain import MessageChain
from graia.application.message.parser.kanata import Kanata
from graia.application.message.parser.signature import FullMatch
from graia.application.group import Group, Member
from expand import judge
from core import get
import aiohttp
import base64
import matplotlib
matplotlib.set_loglevel('info')
import matplotlib.pyplot as plt
import platform
import numpy as np
from io import BytesIO
if platform.system() == 'Windows':
    plt.rcParams['font.sans-serif'] = ['SimHei']
elif platform.system() == 'Linux':
    plt.rcParams['font.sans-serif'] = ['WenQuanYi Zen Hei']

__plugin_name__ = '新冠病毒查看'
__plugin_usage__ = '"COVID-19"'

bcc = get.bcc()
@bcc.receiver(GroupMessage, headless_decoraters = [Depend(judge.active_check_message)],
                            dispatchers = [Kanata([FullMatch('COVID-19')])])
async def COVID(app: GraiaMiraiApplication, group: Group, message: MessageChain, member:Member):
    back = await get_COVID_19()
    await app.sendGroupMessage(group, MessageChain.create([
        Plain("新型冠状病毒前10:\n"+"\n".join(back[0])),
        Image.fromUnsafeBytes(back[1])
        ]))

async def get_COVID_19(Pic=True):
    country_get=[]
    headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                       'Chrome/81.0.4044.69 Safari/537.36 Edg/81.0.416.34'}
    async with aiohttp.request("GET","https://c.m.163.com/ug/api/wuhan/app/data/list-total",headers=headers) as r:
        reponse = await r.json()
    for country in reponse['data']['areaTree']:
        country_get.append([country['name'],country['total']['confirm'],
                            country['today']['confirm'],country['lastUpdateTime']])
    country_get.sort(key=lambda s:s[1],reverse = True)
    get=[f"{a[0]}:{a[1]}例 新增{a[2]}\n{a[3]}" for a in country_get[:10]]
    x=[a[0] for a in country_get[:20]]
    y1=[a[1]-a[2] if a[2] != None else a[1] for a in country_get[:20]]
    y2=[a[2] if a[2] != None else 0 for a in country_get[:20]]
    if Pic:
        # 创建一个点数为 8 x 6 的窗口, 并设置分辨率为 80像素/每英寸
        plt.figure(figsize=(30, 20), dpi=100)
        plt.style.use("dark_background")
        # 再创建一个规格为 1 x 1 的子图
        # plt.subplot(1, 1, 1)
        # 柱子总数
        N = 20
        # 包含每个柱子下标的序列
        index = np.arange(N)
        # 柱子的宽度
        width = 0.5
        # 绘制柱状图, 每根柱子的颜色
        plt.bar(index, y1, width, label="昨日累计人数", color="#FF0000")
        plt.bar(index, y2, width, label="今日新增人数", color="#FF8C00",bottom=y1)
        # 设置横轴标签
        plt.xlabel('各个国家')
        # 设置纵轴标签
        plt.ylabel('累计感染人数')
        # 添加标题
        plt.title('各国新冠病毒感染人数排行')
        # 添加纵横轴的刻度
        plt.xticks(index, x)
        # 添加图例
        plt.legend(loc="upper right")
        

        for a, b, c in zip(index, y1, y2):
            plt.text(a, b + c + 0.05 , str(b + c),
             ha='center', va='bottom', fontsize=10)

        read = BytesIO()
        plt.savefig(read, format = "png", bbox_inches='tight')
        plt.clf()
        return [get,read.getvalue()]
    else:
        return get
