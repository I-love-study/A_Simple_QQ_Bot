from graia.application import GraiaMiraiApplication
from graia.application.event.messages import GroupMessage
from graia.application.message.elements.internal import *
from graia.application.message.chain import MessageChain
from graia.application.message.parser.kanata import Kanata
from graia.application.message.parser.signature import FullMatch, RequireParam
from graia.application.group import Group, Member
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

channel = Channel.current()

data_path = Path(__file__).parent / 'dd_info.yml'

@channel.use(ListenerSchema(
    listening_events=[GroupMessage],
    inline_dispatchers=[Kanata([FullMatch('组织添加 '), RequireParam('tag')])]
    ))
async def dd_group_add(app: GraiaMiraiApplication, group: Group, member: Member, tag: MessageChain):
	name = tag.asDisplay().strip()
	dd_data = yaml.safe_load(data_path.read_text(encoding = 'UTF-8'))
	dd_data.append(name)
	data_path.write_text(yaml.safe_dump(dd_data), encoding = 'UTF-8')
	await app.sendGroupMessage(group, MessageChain.create([Plain(f'增加团队"{name}"成功')]))

@channel.use(ListenerSchema(
    listening_events=[GroupMessage],
    inline_dispatchers=[Kanata([FullMatch('组织删除 '), RequireParam('tag')])]
    ))
async def dd_group_del(app: GraiaMiraiApplication, group: Group, member: Member, tag: MessageChain):
	name = tag.asDisplay().strip()
	dd_data = yaml.safe_load(data_path.read_text(encoding = 'UTF-8'))
	if name in dd_data:
		del dd_data[name]
		msg = f'删除团队"{name}"成功'
	else:
		msg = 'DD数据中找不到这个组织'
	data_path.write_text(yaml.safe_dump(dd_data), encoding = 'UTF-8')
	await app.sendGroupMessage(group, MessageChain.create([Plain(msg)]))

@channel.use(ListenerSchema(
    listening_events=[GroupMessage],
    inline_dispatchers=[Kanata([FullMatch('组织删除 '), RequireParam('tag')])]
    ))
async def dd_member_add(app: GraiaMiraiApplication, group: Group, member: Member, tag: MessageChain):
	