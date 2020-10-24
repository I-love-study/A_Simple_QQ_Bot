from graia.broadcast.builtin.decoraters import Depend
from graia.application import GraiaMiraiApplication
from graia.application.event.messages import GroupMessage
from graia.application.message.elements.internal import Plain, At
from graia.application.message.chain import MessageChain
from graia.application.message.parser.kanata import Kanata
from graia.application.message.parser.signature import FullMatch
from graia.application.group import Group, Member
from graia.template import Template
from expand import judge
from core import get
import core
import random

bcc = get.bcc()
@bcc.receiver(GroupMessage, headless_decoraters = [Depend(judge.active_check_message)],
							dispatchers = [Kanata([FullMatch('helper')])])
async def helper(app: GraiaMiraiApplication, group: Group, message: MessageChain, member:Member):
	tag = message.asDisplay().replace('helper','').strip()
	print(tag)
	ret = []
	if tag == '':
		ret.append(Plain('功能有:'))
		for single in core.loaded_plugins:
			if single.name:
				ret.append(Plain(f'\n{single.name}'))
		ret.append(Plain('\n详细使用方法请输入 helper [模块]\n如:helper Super DD'))
	else:
		for single in core.loaded_plugins:
			if tag == single.name:
				ret.append(Plain(f'{single.name}\n{single.usage}'))
		if not ret:
			ret.append(Plain('啥玩意儿？'))
	print(ret)
	await app.sendGroupMessage(group, MessageChain.create(ret))