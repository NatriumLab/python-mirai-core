import re
from typing import Union, List, Type
from datetime import timedelta
from pathlib import Path
from uuid import UUID
import json
from .log import create_logger
from functools import partial
import asyncio

from .models.message import BotMessage, ImageType, MessageChain,\
    Source, Image, Quote, Plain, BaseMessageComponent, LocalImage
from .models.events import *
from .models.entity import Friend, Group, GroupSetting, Member, MemberChangeableSetting
from .network import HttpXClient
from .exceptions import AuthenticationException, MiraiException


ImageRegex = {
    "group": r"(?<=\{)([0-9A-Z]{8})\-([0-9A-Z]{4})-([0-9A-Z]{4})-([0-9A-Z]{4})-([0-9A-Z]{12})(?=\}\..*?)",
    "friend": r"(?<=/)([0-9a-z]{8})\-([0-9a-z]{4})-([0-9a-z]{4})-([0-9a-z]{4})-([0-9a-z]{12})"
}


def get_matched_string(regex_result):
    if regex_result:
        return regex_result.string[slice(*regex_result.span())]


class Events(Enum):
    BotOnlineEvent = BotOnlineEvent
    BotOfflineEventActive = BotOfflineEventActive
    BotOfflineEventForce = BotOfflineEventForce
    BotOfflineEventDropped = BotOfflineEventDropped
    BotReloginEvent = BotReloginEvent
    BotGroupPermissionChangeEvent = BotGroupPermissionChangeEvent
    BotMuteEvent = BotMuteEvent
    BotUnmuteEvent = BotUnmuteEvent
    BotJoinGroupEvent = BotJoinGroupEvent

    GroupNameChangeEvent = GroupNameChangeEvent
    GroupEntranceAnnouncementChangeEvent = GroupEntranceAnnouncementChangeEvent
    GroupMuteAllEvent = GroupMuteAllEvent

    # 群设置被修改事件
    GroupAllowAnonymousChatEvent = GroupAllowAnonymousChatEvent  # 群设置 是否允许匿名聊天 被修改
    GroupAllowConfessTalkEvent = GroupAllowConfessTalkEvent  # 坦白说
    GroupAllowMemberInviteEvent = GroupAllowMemberInviteEvent  # 邀请进群

    # 群事件(被 Bot 监听到的, 为被动事件, 其中 Bot 身份为第三方.)
    MemberJoinEvent = MemberJoinEvent
    MemberLeaveEventKick = MemberLeaveEventKick
    MemberLeaveEventQuit = MemberLeaveEventQuit
    MemberCardChangeEvent = MemberCardChangeEvent
    MemberSpecialTitleChangeEvent = MemberSpecialTitleChangeEvent
    MemberPermissionChangeEvent = MemberPermissionChangeEvent
    MemberMuteEvent = MemberMuteEvent
    MemberUnmuteEvent = MemberUnmuteEvent

    FriendMessage = FriendMessage
    GroupMessage = GroupMessage


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
        self.logger = create_logger('Bot')

    def check_session(self):
        if not self.session_key:
            raise AuthenticationException('Session key is not set')

    async def handshake(self):
        await self.auth()
        await self.verify()

    async def auth(self) -> None:
        """
        post auth key, and get session key
        :return: None
        """
        result = await self.session.post('/auth', data={'authKey': self.auth_key})
        self.session_key = result.get('session')

    async def verify(self) -> None:
        self.check_session()
        await self.session.post('/verify',
                                data={
                                    'sessionKey': self.session_key,
                                    'qq':         self.qq
                                })

    async def release(self) -> None:
        self.check_session()
        await self.session.post('/release',
                                data={
                                    'sessionKey': self.session_key,
                                    'qq':         self.qq
                                })

    @staticmethod
    def _handle_target_as(target: Union[Group, Friend, Member, int], as_type: Union[Type[Group], Type[Friend], Type[Member]]):
        """
        convert target to id
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

    async def send_friend_message(self,
                                  friend: Union[Friend, int],
                                  message: Union[
                                      MessageChain,
                                      BaseMessageComponent,
                                      List[BaseMessageComponent],
                                      str
                                  ],
                                  quote_source: Union[int, Source] = None) -> BotMessage:
        self.check_session()
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
        result = await self.session.post('/sendFriendMessage',
                                         data=data)

        return BotMessage.parse_obj(result)

    async def send_group_message(self,
                                 group: Union[Group, int],
                                 message: Union[
                                     MessageChain,
                                     BaseMessageComponent,
                                     List[BaseMessageComponent],
                                     str
                                 ],
                                 quote_source: Union[int, Source] = None) -> BotMessage:
        self.check_session()
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

    async def recall(self, source: Union[Source, int]) -> None:
        self.check_session()
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
    async def groups(self) -> List[Group]:
        self.check_session()
        params = {
            'sessionKey': self.session_key,
        }
        result = await self.session.get('/groupList', params=params)
        return [Group.parse_obj(group_info) for group_info in result]

    @property
    async def friends(self) -> List[Friend]:
        self.check_session()
        params = {
            'sessionKey': self.session_key,
        }
        result = await self.session.get('/friendList', params=params)
        return [Friend.parse_obj(friend_info) for friend_info in result]

    async def get_members(self, target: Union[Group, int]) -> List[Member]:
        self.check_session()
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

    async def upload_image(self, image_type: ImageType, image_path: Union[Path, str]) -> Optional[Image]:
        self.check_session()
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

    async def fetch_message(self, count: int) -> List[Event]:
        self.check_session()
        params = {
            'sessionKey': self.session_key,
            'count':      count
        }
        result = await self.session.get('/fetchMessage', params=params)

        for index in range(len(result)):
            if hasattr(Events, result[index]['type']):  # if Event
                if 'messageChain' in result[index]:  # construct message chain
                    result[index]['messageChain'] = MessageChain.custom_parse(result[index]['messageChain'])
                result[index] = Events[result[index]['type']].value.parse_obj(result[index])
        return result

    async def message_from_id(self, source_id: Union[Source, Quote, int]):
        self.check_session()
        if isinstance(source_id, Source):
            source_id = source_id.id
        elif isinstance(source_id, Quote):
            source_id = source_id.id

        params = {
            'sessionKey': self.session_key,
            'id':         source_id
        }

        result = await self.session.get('/messageFromId', params=params)
        if result.get('type') in (EventTypes.GroupMessageEvent.value, EventTypes.FriendMessageEvent.value):
            if "messageChain" in result:
                result['messageChain'] = MessageChain.custom_parse(result['messageChain'])

            if result.get('type') == EventTypes.GroupMessageEvent.value:
                return GroupMessage.parse_obj(result)
            else:
                return FriendMessage.parse_obj(result)
        else:
            raise TypeError(f'Unknown message type')

    async def mute_all(self, group: Union[Group, int]):
        self.check_session()
        params = {
            'sessionKey': self.session_key,
            'target':     Bot._handle_target_as(target=group, as_type=Group)
        }

        await self.session.get('/muteAll', params=params)

    async def unmute_all(self, group: Union[Group, int]):
        self.check_session()
        params = {
            'sessionKey': self.session_key,
            'target':     Bot._handle_target_as(target=group, as_type=Group)
        }

        await self.session.get('/unmuteAll', params=params)

    async def get_member_info(self, group: Union[Group, int], member: Union[Member, int]):
        self.check_session()
        params = {
            'sessionKey': self.session_key,
            'target':     Bot._handle_target_as(target=group, as_type=Group),
            'memberId':   self._handle_target_as(target=member, as_type=Member)
        }

        result = await self.session.get('/memberInfo', params=params)
        return MemberChangeableSetting.parse_obj(result)

    async def get_bot_member_info(self, group: Union[Group, int]):
        self.check_session()
        return await self.get_member_info(group, self.qq)

    async def set_member_info(self, group: Union[Group, int],
                              member: Union[Member, int],
                              setting: MemberChangeableSetting):
        self.check_session()
        data = {
            'sessionKey': self.session_key,
            'target':     Bot._handle_target_as(target=group, as_type=Group),
            'memberId':   self._handle_target_as(target=member, as_type=Member),
            'info':       json.loads(setting.json())
        }

        await self.session.post('/memberInfo', data=data)

    async def get_group_config(self, group: Union[Group, int]) -> GroupSetting:
        self.check_session()
        params = {
            'sessionKey': self.session_key,
            'target':     Bot._handle_target_as(target=group, as_type=Group),
        }
        result = await self.session.get('/groupConfig', params=params)
        return GroupSetting.parse_obj(result)

    async def set_group_config(self, group: Union[Group, int],
                               config: GroupSetting):
        self.check_session()
        data = {
            'sessionKey': self.session_key,
            'target':     Bot._handle_target_as(target=group, as_type=Group),
            'config':     json.loads(config.json())
        }

        await self.session.post('/groupConfig', data=data)

    async def mute(self, group: Union[Group, int],
                   member: Union[Member, int],
                   time: Union[timedelta, int]):
        self.check_session()
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

    async def unmute(self, group: Union[Group, int],
                     member: Union[Member, int]):
        self.check_session()
        data = {
            'sessionKey': self.session_key,
            'target':     Bot._handle_target_as(target=group, as_type=Group),
            'MemberId':   Bot._handle_target_as(target=member, as_type=Member)
        }
        await self.session.post('/unmute', data=data)

    async def kick(self, group: Union[Group, int],
                     member: Union[Member, int],
                     message: str = ''):
        self.check_session()
        data = {
            'sessionKey': self.session_key,
            'target':     Bot._handle_target_as(target=group, as_type=Group),
            'MemberId':   Bot._handle_target_as(target=member, as_type=Member)
        }
        if message:
            data['msg'] = message

        await self.session.post('/kick', data=data)

    async def _handle_image(self, message: BaseMessageComponent, image_type: ImageType):
        self.check_session()
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
        self.check_session()
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
