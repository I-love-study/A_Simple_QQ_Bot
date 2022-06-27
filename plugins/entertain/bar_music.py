from expand import Netease
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import *
from graia.ariadne.message.parser.twilight import (FullMatch, MatchResult,
                                                   SpacePolicy, Twilight,
                                                   WildcardMatch)
from graia.ariadne.model import Group, Member
from graia.saya import Channel, Saya
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graiax import silkcoder

channel = Channel.current()

channel.name("BarMusic")
channel.description("发送'bar_music [歌曲名]'获取语音音乐")
channel.author("I_love_study")

@channel.use(ListenerSchema(
    listening_events=[GroupMessage],
    inline_dispatchers=[Twilight(
        [FullMatch("bar_music").space(SpacePolicy.FORCE),
         WildcardMatch() @ "para"]
    )]
))
async def bar_music(app: Ariadne, group: Group, para: MatchResult):
    song_name = para.result.display.strip() 
    if song_name == '':
        await app.send_group_message(group, MessageChain('点啥歌？'))
        return
    
    search_data = await Netease.search(song_name)
    try:
        download = await Netease.download_song(search_data[0]['id'])
    except Exception:
        await app.send_group_message(group, MessageChain('不知道为什么，但是我就是放不了'))
        return
    music_b = await silkcoder.async_encode(download, rate=80000, ss=0, t=60)
    await app.send_group_message(group, MessageChain(Voice(data_bytes=music_b)))
