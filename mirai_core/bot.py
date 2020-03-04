import re
from typing import Union, List, Any, Dict, Optional
from datetime import timedelta
from pathlib import Path
from uuid import UUID
import json
from logbook import Logger, DEBUG

from .models.message import FriendMessage, GroupMessage, BotMessage, MessageTypes
from events.external import ExternalEvent, ExternalEvents
from models import Friend, Group, GroupSetting, Member, MemberChangeableSetting
from models.message import MessageChain, Source, Image, Quote, Plain, SendImage
from utils import ImageRegex, ImageType, get_matched_string
from models.message import BaseMessageComponent
from network import HttpXClient
from exceptions import AuthenticationException, MiraiException
from functools import partial


class Bot:
    """
    See https://github.com/mamoe/mirai-api-http for details
    """
    def __init__(self, qq: int, host: str = '127.0.0.1', port: int = 8080, auth_key: str = 'abcdefgh'):
        self.qq = qq
        self.auth_key = auth_key
        self.base_url = f'http://{host}:{port}'
        self.session = HttpXClient(self.base_url)
        self.session_key = ''
        self.logger = Logger('Bot', DEBUG)

    async def handshake(self):
        await self.auth()
        await self.verify()

    @staticmethod
    def _require_session_key(func):
        def checker(self: 'Bot', *args, **kwargs):
            if not self.session_key:
                raise AuthenticationException('Session key is not set')
            func(self, *args, **kwargs)
        return checker

    async def auth(self) -> None:
        """
        post auth key, and get session key
        :return: None
        """
        result = await self.session.post('/auth', data={'authKey': self.auth_key})
        self.session_key = result.get('session')

    @_require_session_key
    async def verify(self) -> None:
        await self.session.post('/verify',
                                data={
                                    'sessionKey': self.session_key,
                                    'qq':         self.qq
                                })

    @_require_session_key
    async def release(self) -> None:
        await self.session.post('/release',
                                data={
                                    'sessionKey': self.session_key,
                                    'qq':         self.qq
                                })

    @staticmethod
    def _handle_target_as(target: Union[Group, Friend, Member, int], as_type: Any[Group, Friend, Member]):
        if isinstance(target, int):
            return target
        elif isinstance(target, as_type):
            return target.id
        else:
            raise ValueError(f'Invalid target as {type(as_type)} object.')

    @_require_session_key
    async def send_friend_message(self,
                                  friend: Union[Friend, int],
                                  message: Union[
                                      MessageChain,
                                      BaseMessageComponent,
                                      List[BaseMessageComponent],
                                      str
                                  ]) -> BotMessage:
        result = (await self.session.post('/sendFriendMessage',
                                          data={
                                              'sessionKey':   self.session_key,
                                              'target':       Bot._handle_target_as(friend, Friend),
                                              'messageChain': await self._handle_message_chain(message, Friend)
                                          }))
        return BotMessage.parse_obj(result)

    @_require_session_key
    async def send_group_message(self,
                                 group: Union[Group, int],
                                 message: Union[
                                     MessageChain,
                                     BaseMessageComponent,
                                     List[BaseMessageComponent],
                                     str
                                 ],
                                 quote_source: Union[int, Source] = None) -> BotMessage:
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
        result = await self.session.post('/sendGroupMessage',
                                         data=data)
        return BotMessage.parse_obj(result)

    @_require_session_key
    async def recall(self, source: Union[Source, int]) -> None:
        data = {
            'sessionKey':   self.session_key,
        }
        if isinstance(source, int):
            data['target'] = source
        elif isinstance(source, Source):
            data['target'] = source.id
        else:
            raise MiraiException('Invalid source argument')

        await self.session.post('/recall', data=data)

    @property
    @_require_session_key
    async def groups(self) -> List[Group]:
        params = {
            'sessionKey': self.session_key,
        }
        result = await self.session.get('/groupList', params=params)
        return [Group.parse_obj(group_info) for group_info in result]

    @property
    @_require_session_key
    async def friends(self) -> List[Friend]:
        params = {
            'sessionKey': self.session_key,
        }
        result = await self.session.get('/friendList', params=params)
        return [Friend.parse_obj(friend_info) for friend_info in result]

    @_require_session_key
    async def get_members(self, target: Union[Group, int]) -> List[Member]:
        if isinstance(target, int):
            group = target
        else:
            group = target.id
        params = {
            'sessionKey': self.session_key,
            'target': group
        }
        result = await self.session.get('/memberList', params=params)
        return [Member.parse_obj(member_info) for member_info in result]

    @_require_session_key
    async def upload_image(self, image_type: ImageType, image_path: Union[Path, str]) -> Optional[Image]:
        if isinstance(image_path, str):
            image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError('Image not found.')

        data = {
            'sessionKey': self.session_key,
            'type':       image_type.value
        }
        result = await self.session.upload('/uploadImage', file=image_path, data=data)
        regex = ImageRegex[image_type]
        uuid_string = re.search(regex, result)
        if uuid_string:
            return Image(imageId=UUID(get_matched_string(uuid_string)))

    @_require_session_key
    async def fetchMessage(self, count: int) -> List[Union[FriendMessage, GroupMessage, ExternalEvent]]:
        params = {
            'sessionKey': self.session_key,
            'count':      count
        }
        result = await self.session.get('/fetchMessage', params=params)

        for index in range(len(result)):
            if result[index]['type'] in MessageTypes:  # if Message
                if 'messageChain' in result[index]:  # construct message chain
                    result[index]['messageChain'] = MessageChain.custom_parse(result[index]['messageChain'])
                result[index] = MessageTypes[result[index]['type']].parse_obj(result[index])

            elif hasattr(ExternalEvents, result[index]['type']):  # if Event
                result[index] = ExternalEvents[result[index]['type']].value.parse_obj(result[index])
        return result

    @_require_session_key
    async def message_from_id(self, source_id: Union[Source, Quote, int]):
        if isinstance(source_id, Source):
            source_id = source_id.id
        elif isinstance(source_id, Quote):
            source_id = source_id.id

        params = {
            'sessionKey': self.session_key,
            'id':         source_id
        }

        result = await self.session.get('/messageFromId', params=params)
        if result.get('type') in MessageTypes:
            if "messageChain" in result:
                result['messageChain'] = MessageChain.custom_parse(result['messageChain'])
            return MessageTypes[result['type']].parse_obj(result)
        else:
            raise TypeError(f'Unknown message type')

    @_require_session_key
    async def mute_all(self, group: Union[Group, int]):
        params = {
            'sessionKey': self.session_key,
            'target':     Bot._handle_target_as(target=group, as_type=Group)
        }

        await self.session.get('/muteAll', params=params)

    @_require_session_key
    async def unmute_all(self, group: Union[Group, int]):
        params = {
            'sessionKey': self.session_key,
            'target':     Bot._handle_target_as(target=group, as_type=Group)
        }

        await self.session.get('/unmuteAll', params=params)

    @_require_session_key
    async def get_member_info(self, group: Union[Group, int], member: Union[Member, int]):
        params = {
            'sessionKey': self.session_key,
            'target':     Bot._handle_target_as(target=group, as_type=Group),
            'memberId':   self._handle_target_as(target=member, as_type=Member)
        }

        result = await self.session.get('/memberInfo', params=params)
        return MemberChangeableSetting.parse_obj(result)

    @_require_session_key
    async def get_bot_member_info(self, group: Union[Group, int]):
        return await self.get_member_info(group, self.qq)

    @_require_session_key
    async def set_member_info(self, group: Union[Group, int],
                              member: Union[Member, int],
                              setting: MemberChangeableSetting):
        data = {
            'sessionKey': self.session_key,
            'target':     Bot._handle_target_as(target=group, as_type=Group),
            'memberId':   self._handle_target_as(target=member, as_type=Member),
            'info':       json.loads(setting.json())
        }

        await self.session.post('/memberInfo', data=data)

    @_require_session_key
    async def get_group_config(self, group: Union[Group, int]) -> GroupSetting:
        params = {
            'sessionKey': self.session_key,
            'target':     Bot._handle_target_as(target=group, as_type=Group),
        }
        result = await self.session.get('/groupConfig', params=params)
        return GroupSetting.parse_obj(result)

    @_require_session_key
    async def set_group_config(self, group: Union[Group, int],
                               config: GroupSetting):
        data = {
            'sessionKey': self.session_key,
            'target':     Bot._handle_target_as(target=group, as_type=Group),
            'config':     json.loads(config.json())
        }

        await self.session.post('/groupConfig', data=data)

    @_require_session_key
    async def mute(self, group: Union[Group, int],
                   member: Union[Member, int],
                   time: Union[timedelta, int]):
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

    @_require_session_key
    async def unmute(self, group: Union[Group, int],
                     member: Union[Member, int]):
        data = {
            'sessionKey': self.session_key,
            'target':     Bot._handle_target_as(target=group, as_type=Group),
            'MemberId':   Bot._handle_target_as(target=member, as_type=Member)
        }
        await self.session.post('/unmute', data=data)

    @_require_session_key
    async def unmute(self, group: Union[Group, int],
                     member: Union[Member, int],
                     message: str = ''):
        data = {
            'sessionKey': self.session_key,
            'target':     Bot._handle_target_as(target=group, as_type=Group),
            'MemberId':   Bot._handle_target_as(target=member, as_type=Member)
        }
        if message:
            data['msg'] = message

        await self.session.post('/kick', data=data)

    async def _handle_image(self, image_type: ImageType, message: BaseMessageComponent):
        if not isinstance(message, SendImage):
            return json.loads(message.json())

        if message.uuid:
            return {
                'type':    'Image',
                'imageId': message.uuid
            }
        else:
            return {
                'type':    'Image',
                'imageId': await self.upload_image(image_type, message.path)
            }

    async def _handle_message_chain(self, message: Union[
        MessageChain,
        BaseMessageComponent,
        List[BaseMessageComponent],
        str
    ], as_type: Any[Group, Friend]) -> List:
        if isinstance(message, MessageChain):
            return json.loads(message.json())
        elif isinstance(message, str):
            return [json.loads(Plain(text=message).json())]
        elif isinstance(message, BaseMessageComponent):
            if as_type == Group:
                image_type = ImageType.Group
            else:
                image_type = ImageType.Friend
            return [await self._handle_image(image_type, message)]
        elif isinstance(message, (tuple, list)):
            if as_type == Group:
                image_type = ImageType.Group
            else:
                image_type = ImageType.Friend
            result = [*map(partial(self._handle_image, image_type=image_type), message)]
            return result
        else:
            raise ValueError('Invalid message')
