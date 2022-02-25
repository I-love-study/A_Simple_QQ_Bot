from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import *
from graia.ariadne.message.parser.twilight import Twilight, FullMatch
from graia.ariadne.model import Group, Member
from graia.broadcast.interrupt import InterruptControl
from graia.broadcast.interrupt.waiter import Waiter
from graia.broadcast.exceptions import ExecutionStop
from graia.broadcast.exceptions import PropagationCancelled
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from decorators import SettingCheck

from aiofile import async_open
import re
import random
import ujson as json

__plugin_name__ = 'reply'
__plugin_usage__ = '#内构函数,不外用'

with open('data/reply.json', 'r', encoding = 'UTF-8') as f:
    reply_data = json.load(f)

origin_data = [b for a in reply_data for b in reply_data[a]]

saya = Saya.current()
channel = Channel.current()
inc = InterruptControl(saya.broadcast)
ultra_admin = saya.access('all_setting')['ultra_administration']

class GroupMessageInterrupt(Waiter.create([GroupMessage])):

    def __init__(self, group: Union[Group, int], member: Union[Member, int]):
        self.group = group if isinstance(group, int) else group.id
        self.member = member if isinstance(member, int) else member.id

    async def detected_event(self, group: Group, member: Member, message: MessageChain):
        if self.group == group.id and self.member == member.id:
            return message

@channel.use(ListenerSchema(listening_events=[GroupMessage], priority=8))
async def normal_reply(app: Ariadne, group: Group, message: MessageChain, member:Member):
    k = message.asDisplay()
    for single in origin_data:
        #本来想用regex库,但实地测试发现re更快点(在fullmatch中)
        if re.fullmatch(single['trigger'], k):
            if 'chance' in single and random.randint(1, single['chance']) != 1:
                return
            await app.sendGroupMessage(group, MessageChain.create([
                At(target = member.id),
                Plain(text = "\n" + single['reply'])
                ]))
            raise PropagationCancelled()

@channel.use(ListenerSchema(
    listening_events=[GroupMessage],
    decorators=[SettingCheck(active_members=ultra_admin)],
    inline_dispatchers=[Twilight([FullMatch("回复设置")])]
))
async def reply_setting(app: Ariadne, group: Group, message: MessageChain, member:Member):
    await app.sendGroupMessage(group, MessageChain.create([
        Plain(f'请选择你想操作的类型：\n'), Plain('\n'.join(list(reply_data)))]))
    msg = await inc.wait(GroupMessageInterrupt(group, member))
    to_dict = msg.asDisplay()
    if to_dict not in list(reply_data):
        await app.sendGroupMessage(group, MessageChain.create([Plain('没有找到这个类型，已取消')]))
        return

    await app.sendGroupMessage(group, MessageChain.create([
        Plain('请写出添加内容\n格式:[触发词(不能有空格)] [频率(1为默认触发,2即1/2)] [返回词]')]))
    msg = await inc.wait(GroupMessageInterrupt(group, member))
    if msg.exclude(Plain,Source).__root__:
        await app.sendGroupMessage(group, MessageChain.create([
            Plain('请不要出现@等非本文，谢谢\n已取消')]))
        return

    write_data = dict()
    data = msg.asDisplay().split(' ', 2)
    print(data)

    if re.escape(data[0]) != data[0]:
        await app.sendGroupMessage(group, MessageChain.create([
            Plain('检测到正则表达式方法，请问填写的是否是正则表达式？(是/否)')]))
        msg = await inc.wait(GroupMessageInterrupt(group, member))
        if msg.asDisplay().strip() == '是':
            write_data['trigger'] = data[0]
        if msg.asDisplay().strip() == '否':
            write_data['trigger'] = re.escape(data[0])
    else:
        write_data['trigger'] = data[0]

    if data[1].isdigit():
        if int(data[1]) != 1:
            write_data['chance'] = int(data[1])
    else:
        await app.sendGroupMessage(group, MessageChain.create([
            Plain('无法识别触发频率，已取消')]))
        return

    print(data[2])
    print(write_data)
    write_data['reply'] = data[2]

    await app.sendGroupMessage(group, MessageChain.create([
        Plain('请最后核实添加关键词'),
        Plain(f'\n存入区域:{to_dict}'),
        Plain(f"\n触发词:{write_data['trigger']}"),
        Plain(f"\n触发频率:{write_data['chance'] if 'chance' in write_data else 1}"),
        Plain(f"\n回复词:{write_data['reply']}"),
        Plain(f'\n回复(是/否)')
        ]))
    msg = await inc.wait(GroupMessageInterrupt(group, member))
    if msg.asDisplay() == '是':
        reply_data[to_dict].append(write_data)
        origin_data.append(write_data)
        async with async_open('data/reply.json', 'w', encoding = 'UTF-8') as f:
            await f.write(json.dumps(reply_data, ensure_ascii = False, indent = 2))
        await app.sendGroupMessage(group, MessageChain.create([Plain('操作完成')]))
    else:
        await app.sendGroupMessage(group, MessageChain.create([Plain('操作已取消')]))

@channel.use(ListenerSchema(
    listening_events=[GroupMessage],
    decorators=[SettingCheck(active_members=ultra_admin)],
    inline_dispatchers=[Twilight([FullMatch("回复删除")])]
))
async def reply_delete(app: Ariadne, group: Group, message: MessageChain, member:Member):
    await app.sendGroupMessage(group, MessageChain.create([
        Plain(f'请选择你想操作的类型：\n'), Plain('\n'.join(list(reply_data)))]))
    msg = await inc.wait(GroupMessageInterrupt(group, member))
    to_dict = msg.asDisplay()
    if to_dict not in list(reply_data):
        await app.sendGroupMessage(group, MessageChain.create([Plain('没有找到这个类型，已取消')]))
        return

    await app.sendGroupMessage(group, MessageChain.create([
        Plain('请选择删除的单词\n'),
        Plain('\n'.join(a['trigger'] for a in reply_data[to_dict]))
        ]))
    msg = await inc.wait(GroupMessageInterrupt(group, member))
    delete_word = msg.asDisplay()
    for a in reply_data[to_dict]:
        if a['trigger'] == delete_word:
            reply_data[to_dict].remove(a)
            origin_data.remove(a)
            async with async_open('data/reply.json', 'w', encoding = 'UTF-8') as f:
                await f.write(json.dumps(reply_data, ensure_ascii = False, indent = 2))
            await app.sendGroupMessage(group, MessageChain.create([Plain('操作成功')]))
            return
    await app.sendGroupMessage(group, MessageChain.create([Plain('操作失败')]))

@channel.use(ListenerSchema(
    listening_events=[GroupMessage],
    decorators=[SettingCheck(active_members=ultra_admin)],
    inline_dispatchers=[Twilight([FullMatch("回复删除")])]
))
async def reply_look(app: Ariadne, group: Group, message: MessageChain, member:Member):
    text = ''
    for a in reply_data:
        text += f'\n{a}:\n'
        text += '\n'.join(b['trigger'] for b in reply_data[a])
        text += '\n'
    await app.sendGroupMessage(group,MessageChain.create([Plain(text)]))