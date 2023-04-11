from .bilibili import schedule_getter as bilibili_schedule_getter
from .bangumi import schedule_getter as bangumi_schedule_getter
from .schedule import update_schedule_check
from .utils import RelativeDate

from typing import Annotated
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image
from graia.ariadne.message.parser.twilight import ResultValue, Twilight, WildcardMatch
from graia.ariadne.model import Group
from graia.saya import Channel
from graiax.shortcut.saya import dispatch, listen

channel = Channel.current()

channel.name("AnimeTimeSchedule")
channel.description("发送anime/anime tomorrow/anime yesterday获取昨/今/明的番剧时刻表")
channel.author("I_love_study")

date_dict = {
        'yesterday': RelativeDate.yesterday,
        'tomorrow': RelativeDate.tomorrow,
        '昨天': RelativeDate.yesterday,
        '明天': RelativeDate.tomorrow
    }
schedule_sources = {
    "bilibili": bilibili_schedule_getter,
    "bangumi": bangumi_schedule_getter
}

@listen(GroupMessage)
@dispatch(Twilight.from_command("[anime|番剧时刻表]", ["para" @ WildcardMatch()]))
async def anime(app: Ariadne, group: Group, para: Annotated[MessageChain, ResultValue()]):
    args = str(para).split(maxsplit=1)
    l = len(args)
    if l == 0:
        schedule_date = RelativeDate.today
        schedule_getter = bilibili_schedule_getter
    elif l == 1:
        if args[0] in date_dict:
            schedule_date = date_dict[args[0]]
            schedule_getter = bilibili_schedule_getter
        elif args[0] in schedule_sources:
            schedule_date = RelativeDate.today
            schedule_getter = schedule_sources[args[0]]
        else:
            await app.send_message(group, MessageChain("未知时间/信息源，请查看使用说明后重试"))
            return
    elif l == 2:
        if args[0] in date_dict and args[1] in schedule_sources:
            schedule_date = date_dict[args[0]]
            schedule_getter = schedule_sources[args[1]]
        else:
            await app.send_message(group, MessageChain("未知时间/信息源，请查看使用说明后重试"))
            return
    else:
        return


    pic = await schedule_getter(schedule_date)
    await app.send_message(group, MessageChain(Image(data_bytes=pic)))