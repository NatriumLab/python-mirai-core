from mirai_core import Bot, Updater
from mirai_core.models import Event, Message

qq = 123456
host = '127.0.0.1'
port = 18080
auth_key = 'abcdefgh'

bot = Bot(qq, host, port, auth_key)
updater = Updater(bot)


# for bot methods, see available methods under mirai_core.Bot
# for event types, see mirai_core.models.events
# for exception types, see mirai_core.exceptions

# this is how handling inbound events looks like
@updater.add_handler([Event.GroupMessage, Event.FriendMessage])
async def handler(event: Event.Event):
    """
    handler for multiple events
    :param event: generic type of event
    if only one type of event is handled by this method, the type hinting should be changed accordingly
    in order to see detailed definition of a certain event, either use isinstance to restrict the type, or change the
    type hinting in event handler's definition
    :return: True for block calling other event handlers for this event, None or False for keep calling the rest
    """
    if isinstance(event, Event.GroupMessage):  # handle different types of events
        await bot.send_message(target=event.sender.group,
                               chat_type=Message.TargetType.Group,
                               message=event.messageChain,
                               quote_source=event.messageChain.get_source())
    elif isinstance(event, Event.FriendMessage):
        await bot.send_message(target=event.sender,
                               chat_type=Message.TargetType.Friend,
                               message=[
                                   Message.Plain(text='test'),
                                   Message.At(target=event.sender),
                                   Message.Image(path='/root/whatever.jpg')
                               ],
                               # friend message can also quoted, but only viewable by QQ, not TIM
                               quote_source=event.messageChain.get_source())

        # in case you want the image id (only available when sending via local path instead of url)
        image = Message.Image(path='/root/whatever.jpg')

        await bot.send_message(target=event.sender,
                               chat_type=Message.TargetType.Friend,
                               message=[
                                   image
                               ],
                               save_image_id=True)
        # image.imageId is what you want to save
        # image.imageId is updated after send
        image_id = image.imageId
# run the updater
updater.run()
