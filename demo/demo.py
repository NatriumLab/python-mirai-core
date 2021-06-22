from mirai_core import Bot, Updater
from mirai_core.models import Event, Message, Types
import logging

logging.root.setLevel(logging.DEBUG)

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
    if isinstance(event, Event.Message):  # handle different types of events
        # echo
        await bot.send_message(target=event.sender,
                               message_type=event.type,
                               message=event.messageChain,
                               quote_source=event.messageChain.get_source())

        # custom message
        message_chain = [
            Message.Plain(text='test')
        ]
        if event.type == Types.MessageType.GROUP:
            message_chain.append(event.member.id)
        image = Message.Image(path='/root/whatever.jpg')
        message_chain.append(image)

        bot_message = await bot.send_message(target=event.sender,
                                             message_type=event.type,
                                             message=message_chain,
                                             # friend message can also quoted, but only viewable by QQ, not TIM
                                             quote_source=event.messageChain.get_source())

        # in case you want the message id for recalling
        print(bot_message.messageId)

        # in case you want the image id (only available when sending via local path instead of url)
        # the image id is available for two weeks from the last time it is used
        image_id = image.imageId
        print(image_id)
        return True
    else:
        logging.debug("Unprocessed event {event}")

# run the updater forever, block the program from exiting
updater.run()
