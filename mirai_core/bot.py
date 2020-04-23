from typing import Union, List, Type, Dict
from datetime import timedelta
from pathlib import Path
import json
from .log import create_logger

from .models.message import BotMessage, ImageType, MessageChain, \
    Source, Image, Quote, Plain, BaseMessageComponent, LocalImage
from .models.events import *
from .models.entity import Friend, Group, GroupSetting, Member, MemberChangeableSetting
from .network import HttpClient
from .exceptions import AuthenticationException, MiraiException, NetworkException, SessionException

__ALL__ = [
    'Bot'
]


def retry_once(func):
    async def wrapper(self, *args, **kwargs):
        try:
            return await func(self, *args, **kwargs)
        except (NetworkException, SessionException, AuthenticationException):
            self.logger.exception('Trying handshake due to the following exception')
        try:
            await self.handshake()
            return await func(self, *args, **kwargs)
        except (NetworkException, SessionException, AuthenticationException):
            self.logger.exception('Unable to handshake')
        return None

    return wrapper


class Bot:
    """
    See https://github.com/mamoe/mirai-api-http for details
    """

    def __init__(self, qq: int, host: str = '127.0.0.1', port: int = 8080, auth_key: str = 'abcdefgh', loop=None):
        self.qq = qq
        self.auth_key = auth_key
        self.base_url = f'http://{host}:{port}'
        self.loop = loop
        self.session = HttpClient(self.base_url, loop=self.loop)
        self.session_key = ''
        self.logger = create_logger('Bot')

    async def handshake(self):
        """
        Authenticate and verify the session_key
        Automatically called if session_key needs to be updated
        """
        await self.auth()
        await self.verify()

    async def auth(self) -> None:
        """
        Post auth_key, and get session_key
        """
        result = await self.session.post('/auth', data={'authKey': self.auth_key})
        self.session_key = result.get('session')

    async def verify(self) -> None:
        """
        Post session_key to verify the session
        """
        await self.session.post('/verify',
                                data={
                                    'sessionKey': self.session_key,
                                    'qq':         self.qq
                                })

    async def release(self) -> None:
        """
        Post session_key to release the session
        Needs to be called manually if Updater is not used
        """
        await self.session.post('/release',
                                data={
                                    'sessionKey': self.session_key,
                                    'qq':         self.qq
                                })

    @staticmethod
    def _handle_target_as(target: Union[Group, Friend, Member, int],
                          as_type: Union[Type[Group], Type[Friend], Type[Member]]):
        """
        Internal use only, convert target to id

        :param target: Union[Group, Friend, Member, int]
        :param as_type: Group, Friend or Member
        :return: id, int
        """
        if isinstance(target, int):
            return target
        elif isinstance(target, as_type):
            return target.id
        else:
            raise ValueError(f'Invalid target as {type(as_type)} object.')

    @retry_once
    async def send_friend_message(self,
                                  friend: Union[Friend, int],
                                  message: Union[
                                      MessageChain,
                                      BaseMessageComponent,
                                      List[BaseMessageComponent],
                                      str
                                  ],
                                  quote_source: Union[int, Source] = None) -> BotMessage:
        """
        Send friend message

        :param friend: int or Friend object as target
        :param message: MessageChain, BaseMessageComponent, List of BaseMessageComponent or str, the content to send
        :param quote_source: int (the 64-bit int) or Source, the message to quote
        :return: BotMessage (contains message id)
        """
        data = {
            'sessionKey':   self.session_key,
            'target':       Bot._handle_target_as(friend, Friend),
            'messageChain': await self._handle_message_chain(message, Friend)
        }
        if quote_source:
            if isinstance(quote_source, int):
                data['quote'] = quote_source
            elif isinstance(quote_source, Source):
                data['quote'] = quote_source.id
        result = await self.session.post('/sendFriendMessage', data=data)

        return BotMessage.parse_obj(result)

    @retry_once
    async def send_group_message(self,
                                 group: Union[Group, int],
                                 message: Union[
                                     MessageChain,
                                     BaseMessageComponent,
                                     List[BaseMessageComponent],
                                     str
                                 ],
                                 quote_source: Union[int, Source] = None) -> BotMessage:
        """
        Send group message

        :param group: int or Group object as target
        :param message: MessageChain, BaseMessageComponent, List of BaseMessageComponent or str, the content to send
        :param quote_source: int (the 64-bit int) or Source, the message to quote
        :return: BotMessage (contains message id)
        """
        data = {
            'sessionKey':   self.session_key,
            'target':       Bot._handle_target_as(group, Group),
            'messageChain': await self._handle_message_chain(message, Group)
        }
        if quote_source:
            if isinstance(quote_source, int):
                data['quote'] = quote_source
            elif isinstance(quote_source, Source):
                data['quote'] = quote_source.id
        result = await self.session.post('/sendGroupMessage', data=data)
        return BotMessage.parse_obj(result)

    @retry_once
    async def recall(self, source: Union[Source, int]) -> None:
        """
        Recall a message
        Success if no exception is raised

        :param source: int (the 64-bit int) or Source
        """
        data = {
            'sessionKey': self.session_key,
        }
        if isinstance(source, int):
            data['target'] = source
        elif isinstance(source, Source):
            data['target'] = source.id
        else:
            raise MiraiException('Invalid source argument')

        await self.session.post('/recall', data=data)

    @property
    @retry_once
    async def groups(self) -> List[Group]:
        """
        Get list of joined groups

        :return: List of Group
        """
        params = {
            'sessionKey': self.session_key,
        }
        result = await self.session.get('/groupList', params=params)
        return [Group.parse_obj(group_info) for group_info in result]

    @property
    @retry_once
    async def friends(self) -> List[Friend]:
        """
        Get list of friends

        :return: List of Friend
        """
        params = {
            'sessionKey': self.session_key,
        }
        result = await self.session.get('/friendList', params=params)
        return [Friend.parse_obj(friend_info) for friend_info in result]

    @retry_once
    async def get_members(self, target: Union[Group, int]) -> List[Member]:
        """
        Get list of members of a group

        :param target: int or Group, the target group
        :return: List of Member
        """
        if isinstance(target, int):
            group = target
        else:
            group = target.id
        params = {
            'sessionKey': self.session_key,
            'target':     group
        }
        result = await self.session.get('/memberList', params=params)
        return [Member.parse_obj(member_info) for member_info in result]

    @retry_once
    async def upload_image(self, image_type: ImageType, image_path: Union[Path, str]) -> Optional[Image]:
        """
        Upload a image to QQ server. The image between group and friend is not exchangeable
        This function can be called separately to acquire image uuids, or automatically if using LocalImage while sending

        :param image_type: ImageType, Friend or Group
        :param image_path: absolute path of the image
        :return: Image object
        """
        if isinstance(image_path, str):
            image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError('Image not found.')

        data = {
            'sessionKey': self.session_key,
            'type':       image_type.value
        }
        result = await self.session.upload('/uploadImage', file=image_path, data=data)
        return Image.parse_obj(result)

    @retry_once
    async def fetch_message(self, count: int) -> List[Event]:
        """
        Fetch a list of messages
        This function is called automatically if using polling instead of websocket

        :param count: maximum count of one fetch
        :return: List of Event
        """
        params = {
            'sessionKey': self.session_key,
            'count':      count
        }
        result = await self.session.get('/fetchMessage', params=params)

        try:
            for index in range(len(result)):
                result[index] = self._parse_event(result[index])
        except:
            self.logger.exception('Unhandled exception')
        return result

    @retry_once
    async def mute_all(self, group: Union[Group, int]) -> None:
        """
        Mute all non admin members in group
        Success if no exception is raised

        :param group: int or Group, the target group
        """
        params = {
            'sessionKey': self.session_key,
            'target':     Bot._handle_target_as(target=group, as_type=Group)
        }

        await self.session.get('/muteAll', params=params)

    @retry_once
    async def unmute_all(self, group: Union[Group, int]) -> None:
        """
        Unmute all non admin members in group
        Success if no exception is raised

        :param group: int or Group, the target group
        """
        params = {
            'sessionKey': self.session_key,
            'target':     Bot._handle_target_as(target=group, as_type=Group)
        }

        await self.session.get('/unmuteAll', params=params)

    @retry_once
    async def get_member_info(self, group: Union[Group, int], member: Union[Member, int]) -> MemberChangeableSetting:
        """
        Get the info of a member

        :param group: int or Group, target group
        :param member: int or Member, target member
        :return: MemberChangeableSetting
        """
        params = {
            'sessionKey': self.session_key,
            'target':     Bot._handle_target_as(target=group, as_type=Group),
            'memberId':   self._handle_target_as(target=member, as_type=Member)
        }

        result = await self.session.get('/memberInfo', params=params)
        return MemberChangeableSetting.parse_obj(result)

    @retry_once
    async def get_bot_member_info(self, group: Union[Group, int]) -> MemberChangeableSetting:
        """
        Get the info of this bot

        :param group: int or Group, target group
        :return: MemberChangeableSetting
        """
        return await self.get_member_info(group, self.qq)

    @retry_once
    async def set_member_info(self, group: Union[Group, int],
                              member: Union[Member, int],
                              setting: MemberChangeableSetting) -> None:
        """
        Set the info of a member
        Success if no exception is raised

        :param group: int or Group, target group
        :param member: int or Member, target member
        :param setting: MemberChangeableSetting, the new settings
        """
        data = {
            'sessionKey': self.session_key,
            'target':     Bot._handle_target_as(target=group, as_type=Group),
            'memberId':   self._handle_target_as(target=member, as_type=Member),
            'info':       json.loads(setting.json())
        }

        await self.session.post('/memberInfo', data=data)

    @retry_once
    async def get_group_config(self, group: Union[Group, int]) -> GroupSetting:
        """
        Get the group config of a group

        :param group: int or Group, target group
        :return: GroupSetting
        """
        params = {
            'sessionKey': self.session_key,
            'target':     Bot._handle_target_as(target=group, as_type=Group),
        }
        result = await self.session.get('/groupConfig', params=params)
        return GroupSetting.parse_obj(result)

    @retry_once
    async def set_group_config(self, group: Union[Group, int],
                               config: GroupSetting) -> None:
        """
        Set the group config of a group
        Success if no exception is raised

        :param group: int or Group, target group
        :param config: GroupSetting
        """
        data = {
            'sessionKey': self.session_key,
            'target':     Bot._handle_target_as(target=group, as_type=Group),
            'config':     json.loads(config.json())
        }

        await self.session.post('/groupConfig', data=data)

    @retry_once
    async def mute(self, group: Union[Group, int],
                   member: Union[Member, int],
                   time: Union[timedelta, int]) -> None:
        """
        Mute a member of a group
        Success if no exception is raised

        :param group: int or Group, target group
        :param member: int or Member, target member
        :param time: int or datetime.timedelta, must between 1 minutes and 30 days
        """
        if isinstance(time, timedelta):
            time = int(time.total_seconds())
        time = min(86400 * 30, max(60, time))  # time should between 1 minutes and 30 days
        data = {
            'sessionKey': self.session_key,
            'target':     Bot._handle_target_as(target=group, as_type=Group),
            'MemberId':   Bot._handle_target_as(target=member, as_type=Member),
            'time':       time
        }
        await self.session.post('/mute', data=data)

    @retry_once
    async def unmute(self, group: Union[Group, int],
                     member: Union[Member, int]) -> None:
        """
        Unmute a member of a group
        Success if no exception is raised

        :param group: int or Group, target group
        :param member: int or Member, target member
        """
        data = {
            'sessionKey': self.session_key,
            'target':     Bot._handle_target_as(target=group, as_type=Group),
            'MemberId':   Bot._handle_target_as(target=member, as_type=Member)
        }
        await self.session.post('/unmute', data=data)

    @retry_once
    async def kick(self, group: Union[Group, int],
                   member: Union[Member, int],
                   message: str = '') -> None:
        """
        Kick a member of a group

        :param group: int or Group, target group
        :param member: int or Member, target member
        :param message: string, message to the member
        """
        data = {
            'sessionKey': self.session_key,
            'target':     Bot._handle_target_as(target=group, as_type=Group),
            'MemberId':   Bot._handle_target_as(target=member, as_type=Member)
        }
        if message:
            data['msg'] = message

        await self.session.post('/kick', data=data)

    @retry_once
    async def respond_request(self,
                              request: Union[NewFriendRequestEvent, MemberJoinRequestEvent],
                              response: Union[NewFriendRequestResponse, MemberJoinRequestResponse],
                              message: str = ''):
        if isinstance(request, NewFriendRequestEvent):
            assert isinstance(response, (NewFriendRequestResponse, int)), f'Response type mismatch'
            response = response.value if isinstance(response, NewFriendRequestResponse) else response
            data = {
                'sessionKey': self.session_key,
                'eventId': request.requestId,
                'fromId':  request.supplicant,
                'groupId': request.sourceGroup,
                'operate': response,
                'message': message
            }
            return await self.session.post('/resp/newFriendRequestEvent', data=data)
        elif isinstance(request, MemberJoinRequestEvent):
            assert isinstance(response, (MemberJoinRequestResponse, int)), f'Response type mismatch'
            response = response.value if isinstance(response, MemberJoinRequestResponse) else response
            data = {
                'sessionKey': self.session_key,
                'eventId': request.requestId,
                'fromId':  request.supplicant,
                'groupId': request.sourceGroup,
                'operate': response,
                'message': message
            }
            return await self.session.post('/resp/memberJoinRequestEvent', data=data)
        else:
            raise TypeError(f'Unsupported event: {str(request)}')

    async def _handle_image(self, message: BaseMessageComponent, image_type: ImageType) -> dict:
        """
        Internal use only
        Convert LocalImage to Image, and everything to json

        :param message: BaseMessageComponent
        :param image_type: ImageType
        :return: json representation
        """
        if not isinstance(message, LocalImage):
            return json.loads(message.json())

        image = await self.upload_image(image_type, message.path)

        return {
            'type':    'Image',
            'imageId': image.imageId
        }

    async def _handle_message_chain(self, message: Union[
        MessageChain,
        BaseMessageComponent,
        List[BaseMessageComponent],
        str
    ], as_type: Union[Type[Group], Type[Friend]]) -> List:
        """
        Internal use only
        Convert MessageChain to json

        :param message: MessageChain
        :param as_type: Group or Friend
        :return: list
        """
        if isinstance(message, MessageChain):
            return json.loads(message.json())
        elif isinstance(message, str):
            return [json.loads(Plain(text=message).json())]
        elif isinstance(message, BaseMessageComponent):
            if as_type == Group:
                image_type = ImageType.Group
            else:
                image_type = ImageType.Friend
            return [await self._handle_image(message, image_type)]
        elif isinstance(message, (tuple, list)):
            if as_type == Group:
                image_type = ImageType.Group
            else:
                image_type = ImageType.Friend
            result = [await self._handle_image(m, image_type=image_type) for m in message]
            return result
        else:
            raise ValueError('Invalid message')

    @retry_once
    async def get_config(self) -> dict:
        """
        Get the config of http api

        :return: config
        """
        params = {
            'sessionKey': self.session_key
        }

        result = await self.session.get('/config', params=params)
        return result

    @retry_once
    async def set_config(self, cache_size: int = 4096, enable_websocket: bool = True) -> None:
        """
        Set the config of http api
        Success if no exception is raised

        :param cache_size: int, the size of message cache
        :param enable_websocket: bool, whether to enable websocket (will disable fetch_message accordingly)
        """
        data = {
            'sessionKey':      self.session_key,
            'cacheSize':       cache_size,
            'enableWebsocket': enable_websocket
        }

        await self.session.post('/config', data=data)

    def _parse_event(self, result) -> Event:
        """
        Internal use only
        Parse event or message from json to Event

        :param result: the json
        :return: Event
        """
        if hasattr(Events, result['type']):  # if Event
            try:
                if 'messageChain' in result:  # construct message chain
                    # parse quote first
                    if len(result['messageChain']) > 1:
                        first_component = result['messageChain'][1]
                        if first_component['type'] == 'Quote':  # FIXME: add the first two message part back
                            result['messageChain'][1]['origin'] = MessageChain.custom_parse(
                                result['messageChain'][1]['origin'])
                            try:
                                del result['messageChain'][2]  # delete duplicated at
                                if result['messageChain'][2]['type'] == 'Plain' and result['messageChain'][2]['text'] == ' ':
                                    del result['messageChain'][2]  # delete space after duplicated at
                            except:
                                self.logger.exception('Please open a github issue to report this error')
                    # for idx, component in enumerate(result['messageChain']):
                    #     if component['type'] == 'Quote':
                    #         result['messageChain'][idx]['origin'] = MessageChain.custom_parse(
                    #             result['messageChain'][idx]['origin'])
                    result['messageChain'] = MessageChain.custom_parse(result['messageChain'])
                result = Events[result['type']].value.parse_obj(result)
            except:
                self.logger.exception('Unhandled exception')
            return result
        else:
            raise ValueError('Invalid message chain')

    def _websocket_handler(self, handler: callable) -> callable:
        """
        Internal use only
        Wrap the handler, and convert json to Event

        :param handler: callable, the handler
        :return: wrapped handler
        """

        async def _handler(result: Union[List, Dict]):
            """
            an example handler for create_websocket
            :param result: json
            """
            result = self._parse_event(result)
            await handler(result)

        return _handler

    @retry_once
    async def create_websocket(self, handler, ws_close_handler=None, listen: str = 'all') -> None:
        """
        Register callback for websocket. Once an Event or Message is received, the handler will be invoked

        :param handler: callable
        :param ws_close_handler: callable, websocket shutdown hook
        :param listen: 'all', 'event' or 'message'
        """
        if listen not in ('all', 'event', 'message'):
            raise ValueError("listen must be one of 'all', 'event' or 'message'")
        if ws_close_handler is None:
            async def ws_close_handler(event):
                pass
        await self.session.websocket(f'/{listen}?sessionKey={self.session_key}',
                                     self._websocket_handler(handler), ws_close_handler)
