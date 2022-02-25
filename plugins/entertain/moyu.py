from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import *
from graia.saya import Saya, Channel
from graia.scheduler import timers
from graia.scheduler.saya.schema import SchedulerSchema

from typing import Optional
from datetime import date, timedelta
from itertools import takewhile, dropwhile

saya = Saya.current()
channel = Channel.current()

# 来自《国务院办公厅关于2022年部分节假日安排的通知》
holiday = {
    "元旦": [date(2022, 1, 1), date(2022, 1, 3)],
    "春节": [date(2022, 1, 31), date(2022, 2, 6)],
    "清明节": [date(2022, 4, 3), date(2022, 4, 5)],
    "劳动节": [date(2022, 4, 30), date(2022, 5, 4)],
    "端午节": [date(2022, 6, 3), date(2022, 6, 5)],
    "中秋节": [date(2022, 9, 10), date(2022, 9, 12)],
    "国庆节": [date(2022, 10, 1), date(2022, 10, 7)]
}

# 周末上班
weekend_but_work = {
    # 春节
    date(2022, 1, 29),
    date(2022, 1, 30),
    # 清明节
    date(2022, 4, 2),
    # 劳动节
    date(2022, 4, 24),
    date(2022, 5, 7),
    # 国庆节
    date(2022, 10, 8),
    date(2022, 10, 9)
}

def next_weekend() -> Optional[date]:
    now = date.today()

    # 现在就是周末
    if now.isoweekday() in [6, 7]:
        return

    weekend = now + timedelta(days=6 - now.isoweekday())

    while True:
        # 是调休，不能算是周末
        if weekend in weekend_but_work:
            w = weekend.isoweekday()
            weekend += timedelta(days=1 if w == 6 else 6)
            continue
        
        for _, [f, t] in holiday.items():
            # 这是假期，超越了周末
            if f < weekend < t:
                weekend += timedelta(days=1 if w == 6 else 6)
                continue
        break
    
    return weekend


def in_holiday() -> bool:
    now = date.today()
    for _, [f, t] in holiday.items():
        if f < now < t:
            return True
    return False

@channel.use(SchedulerSchema(timers.crontabify("0 8 * * * *")))
async def moyu(app: Ariadne):
    today = date.today()
    msg = MessageChain.create(
        f"早上好，摸鱼人！今天是{today.strftime('%Y年%m月%d日')}")

    # 看看今天是不是周末
    if today.isoweekday() in [6, 7]:
        msg += "\n今天是周末，"
        if today in weekend_but_work:
            msg += "但很可惜，是要上班desu"
        elif in_holiday():
            msg += "而且还是放假期间哦"
        else:
            msg += "好好休息一下吧"
    else:
        if in_holiday():
            msg += "现在是假期哦~"
    
    end_holiday = list(dropwhile(lambda x: x[1][1] < today, holiday.items()))
    if weekend := next_weekend():
        i = len(list(takewhile(lambda x: x[1][1] < today, end_holiday)))
        end_holiday.insert(i, ("周末", [weekend]))
    
    msg += "\n\n"

    for n, (day, f) in enumerate(end_holiday, 1):
        if n > 3:
            break
        
        f = f[0]
        msg += f"距离{day}还有{(f - today).days}天\n"

    g = saya.access('group_setting').get_active_group(__name__)

    if 806724946 in g:
        g.remove(806724946)

    for sg in g:
        await app.sendGroupMessage(sg, msg)