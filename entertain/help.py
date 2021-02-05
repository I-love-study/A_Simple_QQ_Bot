from graia.application import GraiaMiraiApplication
from graia.application.event.messages import GroupMessage
from graia.application.message.elements.internal import Plain
from graia.application.message.chain import MessageChain
from graia.application.message.parser.kanata import Kanata
from graia.application.message.parser.signature import RegexMatch
from graia.application.group import Group, Member
from core import judge
from core import get
import core

bcc = get.bcc()
@bcc.receiver(GroupMessage, headless_decoraters = [judge.config_check(__name__)],
							dispatchers = [Kanata([RegexMatch('helper.*')])])
async def helper(app: GraiaMiraiApplication, group: Group, message: MessageChain, member:Member):
	tag = message.asDisplay().replace('helper','').strip()
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
	await app.sendGroupMessage(group, MessageChain.create(ret))