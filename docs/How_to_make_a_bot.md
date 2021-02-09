# 如何用Graia做一个能用的bot

### 注意：本文档只会教你怎么做出一个**可以运行**的Bot，并不会教你太多关于Application和Broadcast Control的深度运用。如果想学习更多的关于Graia的用法，我十分建议在Github上搜索以下别人如何用Graia写Bot的。

#

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
