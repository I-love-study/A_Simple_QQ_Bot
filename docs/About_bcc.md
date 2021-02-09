# 关于Broadcast Control

还记得在开头说过的`@bcc.receiver(Event)`吗

## 什么是Broadcast Control
这，是`Broadcast Control`的注册函数，让我们引用[GraiaProject](https://github.com/GraiaProject/Application)作者[GreyElaina](https://github.com/GreyElaina)对其的介绍
>在我们所处的世界是, 从抽象的角度上讲, 每时每刻, 包括我写这个文档的时候, 你读这段文字的时候, 在每一时刻都发生着无数的 "事件", 即 Event.  
Broadcast Control 是基于 Python 标准库中模块 asyncio 的 观察者模式(Observer Pattern) 实现. 在该库中不仅包括完整的监听控制, 事件传播干涉等机制, 还有一套高层封装的 参数解析(Argument Dispatch) 实现.

说简单点，就是通过`bcc.receiver`这个修饰器，将你的函数注册到bcc(Broadcast Control，下同)中，然后当bcc接收到这个事件后，就运行注册的这个函数。

>提醒一下，`graia-application-mirai`的所有事件都存放在`application/event`中  
如果你想注册一个属于你自己的事件，请看[自定义事件](https://graia-document.vercel.app/docs/broadcast-control/bcc-custom-event)

## 关于无头修饰器(headless_decorators)

让我们假设一个场景：  
你要做一个群管bot，然后你写了很多个Listener用来接收管理员发出的命令，写到最后你发现你所有的Listener里都有一段用于判断操作者是否是管理员的操作
```python
from graia.application.group import Member, MemberPerm

@bcc.receicer(GroupMessage)
async def admin_command(member: Member):
    if member.permission == MemberPerm.Member:
        return
    ...
```
这好吗？这不好，所以有什么办法呢？这个时候我们就可以时候无头修饰器(headless_decorators)了

### 怎么用
我们把上面的管理函数再重新写一遍
```python
from graia.broadcast.builtin.decorators import Depend
from graia.broadcast.exceptions import ExecutionStop
from graia.application.group import Member, MemberPerm

@Depend
async def check_admin(member: Member):
    if member.permission == MemberPerm.Member:
        raise ExecutionStop()

@bcc.receicer(GroupMessage, headless_decorators=[check_admin])
async def admin_command(member: Member):
    ...
```
这样是不是清爽多了
