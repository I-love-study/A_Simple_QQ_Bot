from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.parser.base import MatchContent
from graia.ariadne.model import Group
from graia.saya import Channel
from graiax.shortcut.saya import listen, decorate
import random

channel = Channel.current()

channel.name("Material")
channel.description("发送'learn'获取学❤习❤资❤料")
channel.author("I_love_study")
#这些都是厚大法考的学习资料

@listen(GroupMessage)
@decorate(MatchContent("learn"))
async def learn(app: Ariadne, group: Group):
    if random.randint(0,4) != 0:
        await app.send_group_message(group, MessageChain(
            "你好惨哦\n没有学习资料看\n可惜了你没抽到呢"))
    else:
        learning_urls=[
            'http://oss.fk.houdask.com/sys/v/19/10/f64809ee7ccd44319ffddf74c8c8abf7.rar',
            'http://oss.fk.houdask.com/sys/v/19/10/3f036ac7d1fc4912b2a11331c3ef33c5.rar',
            'http://oss.fk.houdask.com/sys/v/19/10/461c32c3904e44f08b721600fcf32fb7.rar',
            'http://oss.fk.houdask.com/sys/v/19/10/192c231fc56c4ca09bffe69856dba705.rar',
            'http://oss.fk.houdask.com/sys/v/20/01/5cdc62ab47e1460789a0cd691b572415.zip',
            'http://oss.fk.houdask.com/sys/v/20/01/24901a9ebeab4ac5a8bc551572af8c24.zip',
            'http://oss.fk.houdask.com/sys/v/20/01/e48ea55b6c8147a9ac90ced8ef3bc80e.rar',
            'http://oss.fk.houdask.com/sys/v/20/01/10ebebeae4d14f6aa786537b3adc374d.zip',
            'http://oss.fk.houdask.com/sys/v/20/01/51dc2a25b3474022b982191174dda41c.zip',
            'http://oss.fk.houdask.com/sys/v/20/01/1043c2175f84478baa8be09ed92aac7c.zip',
            'http://oss.fk.houdask.com/sys/v/20/01/d15be5ac6027461794e399402bb8ddec.rar',
            'http://oss.fk.houdask.com/sys/v/20/01/0dd665e49ec24999b772475fbf78a65a.zip']
        await app.send_group_message(group, MessageChain(
            "学❤习❤资❤料\n请❤勿❤外❤传\n" + random.choice(learning_urls)))