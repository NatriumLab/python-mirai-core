# Mirai HTTP 开发包

由 [Python-Mirai](https://github.com/Chenwe-i-lin/python-mirai) 早期版本重写而来。
如果 **Star** 本项目，请同时 **Star** 原项目。

精简版 [Mirai-HTTP-API](https://github.com/mamoe/mirai-api-http) SDK

英文文档： [Here](https://mirai-py.originpages.com/python-mirai-core/docs/mirai_core/index.html) 

如果您使用 PyCharm 书写代码，那么仅依靠 PyCharm 的提示即可获得与上述文档相同的内容。

与 mirai core 1.0RC 保持同步

## 安装

### 从 PyPI 安装

``` bash
pip install python-mirai-core
```

### 从 GitHub 安装

``` bash
pip install git+git:://github.com/NatriumLab/python-mirai-core
```

### 简要说明

`Bot` 和 `Updater` 是核心类型。

`Bot` 包含所有向外发出的操作 (比如 `send_message`),

`Updater` 包含所有接收事件的操作 (例如监听好友消息)。

所有事件的定义在 `mirai_core.models.Event`
 
所有消息组件的定义在 `mirai_core.models.Message`

### 功能

- 断线自动重连，自动创建websocket

- 与 python-telegram-bot 和 aiogram 的开发体验接近

- 于原有 HTTP API 相比，合并了发送和接收来自"好友"，"群"，"临时对话"的逻辑，使代码更加简单。

- 允许多个 handler 串行监听同一事件, 通过 `return True` 阻止事件继续向后传递

### 例子

```python
from mirai_core import Bot, Updater
from mirai_core.models import Event, Message, Types

qq = 123456
host = '127.0.0.1'
port = 18080
auth_key = 'abcdefgh'
protocol = 'https'

bot = Bot(qq, host, port, auth_key, protocol=protocol)
updater = Updater(bot)


# for bot methods, see available methods under mirai_core.Bot
# for event types, see mirai_core.models.Event
# for enums, see mirai_core.models.Types
# for exception types, see mirai_core.exceptions

# 一个简单的消息接收与发送
@updater.add_handler([Event.Message])
async def handler(event: Event.BaseEvent):
    """
    handler for multiple events

    :param event: generic type of event
    if only one type of event is handled by this method, the type hinting should be changed accordingly

    e.g. async def handler(event: BaseEvent.Message):

    in order to see detailed definition of a certain event, either use isinstance to restrict the type, or change the
    type hinting in event handler's definition

    e.g. if isinstance(event, BaseEvent.Message):

    :return: True for block calling other event handlers for this event, None or False for keep calling the rest
    """
    if isinstance(event, Event.Message):  # 通过 isinstance 激活具体类型的补全
        # 现在可以通过键入 "event." 查看 event 的所有可用属性
        # 复读示例
        await bot.send_message(target=event.sender,
                               message_type=event.type,
                               message=event.messageChain,
                               quote_source=event.messageChain.get_source())

        # 自定义消息链
        # 所有可用消息链内容在 mirai_core.models.Message 下
        message_chain = [
            # 输入 Message.Plain( 并停顿，即可看到 PyCharm 补全的参数列表
            Message.Plain(text='test')
        ]
        if event.type == Types.MessageType.GROUP:
            message_chain.append(event.member.id)
        image = Message.Image(path='/root/whatever.jpg')
        message_chain.append(image)
        
        # 输入 bot.send_message( 并停顿，即可看到 PyCharm 补全的参数列表
        bot_message = await bot.send_message(target=event.sender,
                                             message_type=event.type,
                                             message=message_chain,
                                             # 好友消息也可以quote，但只有qq可见，tim不可见
                                             quote_source=event.messageChain.get_source())

        # 如果需要消息id，通过如下方式获取
        print(bot_message.messageId)

        # 如果需要图片id （便于以后发送）
        # 图片 id 有效期为自最后一次使用两周
        image_id = image.imageId
        print(image_id)
        return True

# 启动并阻塞进程，防止退出
updater.run()

```

更加复杂的例子: 见 [UMR](https://github.com/JQ-Networks/UMRMiraiDriver/blob/master/umr_mirai_driver/driver.py)

### 感谢 

这段懒得翻译了

Thanks [`mamoe`](https://github.com/mamoe) brings us [`mirai`](https://github.com/mamoe/mirai), a tremendous work that 
enables boundless possibilities for QQ Bots. 

Thanks [`Python-Mirai`](https://github.com/NatriumLab/python-mirai/) for inspirations and data parsing.

### License

[`GNU AGPLv3`](https://choosealicense.com/licenses/agpl-3.0/) 
 
Same as [`mirai`](https://github.com/mamoe/mirai) 
