from graia.ariadne.app import Ariadne
from graia.saya import Channel
from graia.ariadne.message.parser.twilight import Twilight, MatchResult
from graia.ariadne.console.saya import ConsoleSchema

from loguru import logger

channel = Channel.current()

@channel.use(ConsoleSchema([Twilight.from_command("group_chat {g} {msg}")]))
async def console_chat(app: Ariadne, g: MatchResult, msg: MatchResult):
    group_id = g.result.display
    if not group_id.isdigit(): 
        logger.error(f"{group_id} is not a group id")
    elif not msg.result: 
        logger.error("您消息呢？")
    else:
        await app.send_group_message(int(group_id), msg.result)