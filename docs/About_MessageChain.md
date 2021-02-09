# 关于MessageChain

当你在看到第一个示例发送信息时用的MessageChain的时候，你一定一脸懵逼吧(就是下面这个)
```python
MessageChain.create([Plain('你好')])
```
## 什么是MessageChain
消息链(MessageChain)是Mirai中用于发送消息的一个列表，用来更好的发送和接收来自QQ的富文本消息(如图片，@等)

### 为什么不能采用像CQ码一样用Mirai码发送呢
1. 不像CQ码，Mirai码并不能提供完整的信息  
   比如图片的CQ码是`[mirai:image:$imageId]`,里面并不能包含包括图片url等信息
2. 基本断绝了消息解析的bug  
   假设你之前用过酷Q，你就会知道CQ码注入的问题，但是在Mirai中，这类问题存在的可能性就基本为0了

### MessageChain有什么方法
让我们直接引用源码中的注释  
~~Graia真是一个源码注释比文档还长的~~

  1. 你可以使用 `MessageChain.create` 方法创建一个消息链:
      ``` python
      MessageChain.create([
          Plain("这是盛放在这个消息链中的一个 Plain 元素")
      ])
      ```
  2. 你可以使用 `MessageChain.isImmutable` 方法判定消息链的可变型:
      ``` python
      print(message.isImmutable()) # 监听器获取到的消息链默认为 False.
      ```
  3. 你可以使用 `MessageChain.asMutable` 和 `MessageChain.asImmutable` 方法分别获得可变与不可变的消息链.
  4. 你可以使用 `MessageChain.isSendable` 方法检查消息链是否可以被 **完整无误** 的发送.
  5. 使用 `MessageChain.asSendable` 方法, 将自动过滤原消息链中的无法发送的元素, 并返回一个新的, 可被发送的消息链.
  6. `MessageChain.has` 方法可用于判断特定的元素类型是否存在于消息链中:
      ``` python
      print(message.has(At))
      # 使用 in 运算符也可以
      print(At in message)
      ```
  7. 可以使用 `MessageChain.get` 方法获取消息链中的所有特定类型的元素:
      ``` python
      print(message.get(Image)) # -> List[Image]
      # 使用类似取出列表中元素的形式也可以:
      print(message[Image]) # -> List[Image]
      ```
  8. 使用 `MessageChain.asDisplay` 方法可以获取到字符串形式表示的消息, 至于字面意思, 看示例:
      ``` python
      print(MessageChain.create([
          Plain("text"), At(123, display="某人"), Image(...)
      ]).asDisplay()) # -> "text@某人 [图片]"
      ```
  9. 使用 `MessageChain.join` 方法可以拼接多个消息链:
      ``` python
      MessageChain.join(
          message1, message2, message3, ...
      ) # -> MessageChain
      ```
  10. `MessageChain.plusWith` 方法将在现有的基础上将另一消息链拼接到原来实例的尾部, 并生成, 返回新的实例; 该方法不改变原有和传入的实例.
  11. `MessageChain.plus` 方法将在现有的基础上将另一消息链拼接到原来实例的尾部; 该方法更改了原有的实例, 并要求 `isMutable` 方法返回 `True` 才可以执行.
  12. `MessageChain.asSerializationString` 方法可将消息链对象转为以 "Mirai 码" 表示特殊对象的字符串
  13. `MessageChain.fromSerializationString` 方法可以从以 "Mirai 码" 表示特殊对象的字符串解析为消息链, 不过可能不完整.
  14. `MessageChain.asMerged` 方法可以将消息链中相邻的 Plain 元素合并为一个 Plain 元素.
  15. 你可以通过一个分片实例取项, 这个分片的 `start` 和 `end` 的 Type Annotation 都是 `Optional[MessageIndex]`:
      ``` python
      message = MessageChain.create([
          Plain("123456789"), At(123), Plain("3423")
      ])
      message.asMerged()[(0, 12):] # => [At(123), Plain("3423")]
      ```
  16. `MessageChain.getFirst` 方法获取消息链中第 1 个特定类型的消息元素
  17. `MessageChain.getOne` 方法获取消息链中第 index + 1 个特定类型的消息元素

### MessageChain中有什么元素
>注：以下Element都能在`graia.application.message.elements.internal`中找到  
由于`Mirai-api-http`一直在🕊，所以有些Mirai已经支持的Element并不能在Graia使用(套娃的坏处)

目前Graia所支持的Element有以下几个：

Element | 作用 |手搓栗子(x为不支持手搓)
---|:--:|:--:
Plain | 承载消息中的文字 | Plain('你好')
Source | 消息在一个特定聊天区域内的唯一标识 | x
Quote | 消息中回复其他消息/用户的部分 | x(若要回复，app.sendGroupMesage方法有quote参数)
At | 消息中用于提醒/呼唤特定用户 | At(114514)
AtAll | 群组中的管理员提醒群组中的所有成员 | AtAll()
Face | 消息中所附带的表情(内置) | Face(123)
Image | 消息中所附带的图片 | *有点复杂，下面有详细介绍
FlashImage | 闪照 | *有点复杂，下面有详细介绍
Voice | 语音 | Voice.fromLocalFile(file) *只支持群语音且≤1Mb
Xml | Xml卡片(合并消息是这个) | 暂无栗子
Json | Json卡片 | 暂无栗子
App | App卡片(一般App转发都是这个) | 暂无栗子
Poke | 戳一戳 | Poke(PokeMethods.FangDaZhao)

  
### 关于Image,FlashImage的接收和发送

接收的时候，你的Image元素应该会有imageIdurl这俩个参数  
如果你想要获取图片本身，请使用`await Image.http_to_bytes()`方法获取图片的二进制数据

发送的时候，我们有以下几种方法

函数 | 作用 | 参数
:--:|:--:|:--:
fromLocalFile | 从本地文件创建 | 支持str和pathlib.Path 实例
fromUnsafeBytes | 从二进制数据创建 | 支持任意bytes
fromUnsafePath | 让`Mirai-api-htp`从本地文件创建 | 支持str和pathlib.Path
fromNetworkAddress | 从网络创建 | 支持str

而FlashImage的发送方法，就是再加一个`asFlash()`  
e.g: `Image.fromLocalFile("./flashimage.png").asFlash()`