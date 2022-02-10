from graia.ariadne.app import Ariadne
from graia.saya import Channel
from graia.ariadne.message.parser.twilight import Sparkle, Twilight, ParamMatch
from graia.ariadne.console.saya import ConsoleSchema

from loguru import logger

channel = Channel.current()

@channel.use(ConsoleSchema([Twilight.from_command("group_chat {0} {1}")]))
async def console_chat(app: Ariadne, sparkle: Sparkle):
    group, message = sparkle[ParamMatch]
    group_id = group.result.asDisplay()
    if not group_id.isdigit(): 
        logger.error(f"{group.result.asDisplay()} is not a group id")
    elif not message.result: 
        logger.error("您消息呢？")
    else:
        await app.sendGroupMessage(int(group_id), message.result)