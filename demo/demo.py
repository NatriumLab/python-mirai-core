from mirai_core import Bot, Updater
from mirai_core.models import events, message

qq = 123456
host = '127.0.0.1'
port = 18080
auth_key = 'abcdefgh'

bot = Bot(qq, host, port, auth_key)
updater = Updater(bot)


@updater.add_handler([events.GroupMessage, events.FriendMessage])
async def handle(event: events.Event):
    if isinstance(event, events.GroupMessage):
        await bot.send_group_message(group=event.sender.group,
                                     message=event.messageChain,
                                     quote_source=event.messageChain.get_source())
    elif isinstance(event, events.FriendMessage):
        await bot.send_friend_message(friend=event.sender,
                                      message=[
                                          message.Plain(text='test'),
                                          message.At(target=event.sender),
                                          message.SendImage(path='/root/whatever.jpg')
                                      ])

updater.run()
