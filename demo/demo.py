from mirai_core import Bot, Updater
from mirai_core.models import events, message

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
@updater.add_handler([events.GroupMessage, events.FriendMessage])
async def handler(event: events.Event):
    """
    handler for multiple events
    :param event: generic type of event
    if only one type of event is handled by this method, the type hinting should be changed accordingly
    in order to see detailed definition of a certain event, either use isinstance to restrict the type, or change the
    type hinting in event handler's definition
    :return: True for block calling other event handlers for this event, None or False for keep calling the rest
    """
    if isinstance(event, events.GroupMessage):  # handle different types of events
        await bot.send_group_message(group=event.sender.group,
                                     message=event.messageChain,
                                     quote_source=event.messageChain.get_source())
    elif isinstance(event, events.FriendMessage):
        await bot.send_friend_message(friend=event.sender,
                                      message=[
                                          message.Plain(text='test'),
                                          message.At(target=event.sender),
                                          message.LocalImage(path='/root/whatever.jpg')
                                      ],
                                      # friend message can also quoted, but only viewable by QQ, not TIM
                                      quote_source=event.messageChain.get_source())
        # or if you want to save image_id
        image = await bot.upload_image(image_type=message.ImageType.Friend, image_path='/root/whatever.jpg')
        # image.imageId is what you want to save
        await bot.send_friend_message(friend=event.sender,
                                      message=[
                                          image
                                      ])

# run the updater
updater.run()
