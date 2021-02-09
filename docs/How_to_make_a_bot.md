# 如何用Graia做一个能用的bot

## 怎么让Graia在你的电脑/服务器运作
请阅读以下几篇文章

[使用Mirai Console Loader(mcl)](https://github.com/iTXTech/mirai-console-loader)
or
[手动配置Mirai Console](https://github.com/mamoe/mirai-console/blob/master/docs/Run.md)

[如何安装Mirai-api-http](https://github.com/project-mirai/mirai-api-http#%E5%AE%89%E8%A3%85mirai-api-http)

[如何配置Graia](https://graia-document.vercel.app/docs/guides/installation)
and
[Graia的配置参数](https://graia-document.vercel.app/docs/guides/about-config)

## 创建一个简单的回复机器人
```python
from graia.application import GraiaMiraiApplication
from graia.application.event.messages import GroupMessage
from graia.application.message.elements.internal import Plain
from graia.application.message.chain import MessageChain
from graia.application.group import Group, Member

@bcc.receiver(GroupMessage)
async def hello_world(app: GraiaMiraiApplication, group: Group, message: MessageChain, member:Member):
    if message.asDisplay() == '你好':
        await app.sendGroupMessage(group, MessageChain.create([Plain('你好')]))
```

通过以上办法，当你在机器人所在的群里发送“你好”，他就会回复你一句你好了

### 这些都是什么跟什么？

`@bcc.receiver(Event)`

这，是`Broadcast Control`的注册函数，让我们引用[GraiaProject](https://github.com/GraiaProject/Application)作者[GreyElaina](https://github.com/GreyElaina)对其的介绍
>在我们所处的世界是, 从抽象的角度上讲, 每时每刻, 包括我写这个文档的时候, 你读这段文字的时候, 在每一时刻都发生着无数的 "事件", 即 Event.  
Broadcast Control 是基于 Python 标准库中模块 asyncio 的 观察者模式(Observer Pattern) 实现. 在该库中不仅包括完整的监听控制, 事件传播干涉等机制, 还有一套高层封装的 参数解析(Argument Dispatch) 实现.

说简单点，就是通过`bcc.receiver`这个修饰器，将你的函数注册到bcc(Broadcast Control，下同)中，然后当bcc接收到这个事件后，就运行注册的这个函数。

>提醒一下，`graia-application-mirai`的所有事件都存放在`application/event`中  
如果你想注册一个属于你自己的事件，请看[自定义事件](https://graia-document.vercel.app/docs/broadcast-control/bcc-custom-event)

