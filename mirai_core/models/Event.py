from pydantic import BaseModel, Field, Extra, root_validator
from .Entity import Permission, Group, Member, Friend
from .Message import MessageChain
from .Types import MessageType
from typing import Optional, Literal, Union, Type, Any
from datetime import datetime


class BaseEvent(BaseModel):
    type: str

    class Config:
        extra = Extra.allow

    def __str__(self):
        return f'[{str(self.json(ensure_ascii=False))}]'


class BotOnlineEvent(BaseEvent):
    type: Literal['BotOnlineEvent']
    qq: int

    def __str__(self):
        return f'[{self.type}: qq={self.qq}]'


class BotOfflineEventActive(BaseEvent):
    type: Literal['BotOfflineEventActive']
    qq: int

    def __str__(self):
        return f'[{self.type}: qq={self.qq}]'


class BotOfflineEventForce(BaseEvent):
    type: Literal['BotOfflineEventForce']
    qq: int

    def __str__(self):
        return f'[{self.type}: qq={self.qq}]'


class BotOfflineEventDropped(BaseEvent):
    type: Literal['BotOfflineEventDropped']
    qq: int

    def __str__(self):
        return f'[{self.type}: qq={self.qq}]'


class BotReloginEvent(BaseEvent):
    type: Literal['BotReloginEvent']
    qq: int

    def __str__(self):
        return f'[{self.type}: qq={self.qq}]'


class BotGroupPermissionChangeEvent(BaseEvent):
    type: Literal['BotGroupPermissionChangeEvent']
    origin: Permission
    current: Permission
    group: Group

    def __str__(self):
        return f'[{self.type}: ' \
               f'origin={repr(self.origin)}, new={repr(self.current)}, group={repr(self.group)}]'


class BotMuteEvent(BaseEvent):
    type: Literal['BotMuteEvent']
    durationSeconds: int
    operator: Optional[Member]

    def __str__(self):
        return f'[{self.type}: durationSeconds={self.durationSeconds}, operator={repr(self.operator)}]'


class BotUnmuteEvent(BaseEvent):
    type: Literal['BotUnmuteEvent']
    operator: Optional[Member]

    def __str__(self):
        return f'[{self.type}: operator={repr(self.operator)}]'


class BotJoinGroupEvent(BaseEvent):
    type: Literal['BotJoinGroupEvent']
    group: Group

    def __str__(self):
        return f'[{self.type}: group={repr(self.group)}]'


class BotLeaveEventActive(BaseEvent):
    type: Literal['BotLeaveEventActive']
    group: Group

    def __str__(self):
        return f'[{self.type}: group={repr(self.group)}]'


class BotLeaveEventKick(BaseEvent):
    type: Literal['BotLeaveEventKick']
    group: Group

    def __str__(self):
        return f'[{self.type}: group={repr(self.group)}]'


class GroupRecallEvent(BaseEvent):
    type: Literal['GroupRecallEvent']
    authorId: int
    messageId: int
    time: datetime
    group: Group
    operator: Optional[Member]

    def __str__(self):
        return f'[{self.type}: authorId={self.authorId}, messageId={self.messageId}, time={self.time},' \
               f' group={repr(self.group)}, operator={repr(self.operator)}]'


class FriendRecallEvent(BaseEvent):
    type: Literal['FriendRecallEvent']
    authorId: int
    messageId: int
    time: int
    operator: int


class GroupNameChangeEvent(BaseEvent):
    type: Literal['GroupNameChangeEvent']
    origin: str
    current: str
    group: Group
    operator: bool

    def __str__(self):
        return f'[{self.type}: ' \
               f'origin={self.origin}, new={self.current}, group={repr(self.group)}, operator={self.operator}]'


class GroupEntranceAnnouncementChangeEvent(BaseEvent):
    type: Literal['GroupEntranceAnnouncementChangeEvent']
    origin: str
    current: str
    group: Group
    operator: Optional[Member]

    def __str__(self):
        return f'[{self.type}: ' \
               f'origin={self.origin}, new={self.current}, group={repr(self.group)}, operator={repr(self.operator)}]'


class GroupMuteAllEvent(BaseEvent):
    type: Literal['GroupMuteAllEvent']
    origin: bool
    current: bool
    group: Group
    operator: Optional[Member]

    def __str__(self):
        return f'[{self.type}: ' \
               f'origin={self.origin}, new={self.current}, group={repr(self.group)}, operator={repr(self.operator)}]'


class GroupAllowAnonymousChatEvent(BaseEvent):
    type: Literal['GroupAllowAnonymousChatEvent']
    origin: bool
    current: bool
    group: Group
    operator: Optional[Member]

    def __str__(self):
        return f'[{self.type}: ' \
               f'origin={self.origin}, new={self.current}, group={repr(self.group)}, operator={repr(self.operator)}]'


class GroupAllowConfessTalkEvent(BaseEvent):
    type: Literal['GroupAllowAnonymousChatEvent']
    origin: bool
    current: bool
    group: Group
    isByBot: bool

    def __str__(self):
        return f'[{self.type}: ' \
               f'origin={self.origin}, new={self.current}, group={repr(self.group)}, isByBot={self.isByBot}]'


class GroupAllowMemberInviteEvent(BaseEvent):
    type: Literal['GroupAllowMemberInviteEvent']
    origin: bool
    current: bool
    group: Group
    operator: Optional[Member]

    def __str__(self):
        return f'[{self.type}: ' \
               f'origin={self.origin}, new={self.current}, group={repr(self.group)}, operator={repr(self.operator)}]'


class MemberJoinEvent(BaseEvent):
    type: Literal['MemberJoinEvent']
    member: Member

    def __str__(self):
        return f'[{self.type}: ' \
               f'member={repr(self.member)}]'


class MemberLeaveEventKick(BaseEvent):
    type: Literal['MemberLeaveEventKick']
    member: Member
    operator: Optional[Member]

    def __str__(self):
        return f'[{self.type}: ' \
               f'member={repr(self.member)}, operator={repr(self.operator)}]'


class MemberLeaveEventQuit(BaseEvent):
    type: Literal['MemberLeaveEventQuit']
    member: Member

    def __str__(self):
        return f'[{self.type}: ' \
               f'member={repr(self.member)}]'


class MemberCardChangeEvent(BaseEvent):
    type: Literal['MemberCardChangeEvent']
    origin: str
    current: str
    member: Member
    operator: Optional[Member]

    def __str__(self):
        return f'[{self.type}: ' \
               f'origin={self.origin}, new={self.current}, member={repr(self.member)}, operator={repr(self.operator)}]'


class MemberSpecialTitleChangeEvent(BaseEvent):
    type: Literal['MemberSpecialTitleChangeEvent']
    origin: str
    current: str
    member: Member

    def __str__(self):
        return f'[{self.type}: ' \
               f'origin={self.origin}, new={self.current}, member={repr(self.member)}]'


class MemberPermissionChangeEvent(BaseEvent):
    type: Literal['MemberPermissionChangeEvent']
    origin: str
    current: str
    member: Member

    def __str__(self):
        return f'[{self.type}: ' \
               f'origin={self.origin}, new={self.current}, member={repr(self.member)}]'


class MemberMuteEvent(BaseEvent):
    type: Literal['MemberMuteEvent']
    durationSeconds: int
    member: Member
    operator: Optional[Member]

    def __str__(self):
        return f'[{self.type}: ' \
               f'durationSeconds={self.durationSeconds}, member={repr(self.member)}, operator={repr(self.operator)}]'


class MemberUnmuteEvent(BaseEvent):
    type: Literal['MemberUnmuteEvent']
    member: Member
    operator: Optional[Member]

    def __str__(self):
        return f'[{self.type}: ' \
               f'member={repr(self.member)}, operator={repr(self.operator)}]'


class Message(BaseEvent):
    # fusion class
    type: MessageType
    messageChain: MessageChain
    sender: Union[Friend, Member]

    def __init__(self, messageChain: MessageChain = None, **kwargs):
        if messageChain:
            messageChain = MessageChain.parse_obj(messageChain)
        super().__init__(messageChain=messageChain, **kwargs)

    @property
    def member(self):
        if isinstance(self.sender, Member):
            return self.sender
        return None

    @property
    def friend(self):
        if isinstance(self.sender, Friend):
            return self.sender
        return None


class NewFriendRequestEvent(BaseEvent):
    type: Literal['NewFriendRequestEvent']
    requestId: int = Field(..., alias="eventId")
    supplicant: int = Field(..., alias="fromId")  # 即请求方 QQ
    sourceGroup: Optional[int] = Field(..., alias="groupId")
    nickname: str = Field(..., alias="nick")


class MemberJoinRequestEvent(BaseEvent):
    type: Literal['MemberJoinRequestEvent']
    requestId: int = Field(..., alias="eventId")
    supplicant: int = Field(..., alias="fromId")  # 即请求方 QQ
    sourceGroup: Optional[int] = Field(..., alias="groupId")
    groupName: str = Field(..., alias="groupName")
    nickname: str = Field(..., alias="nick")


class AuthEvent(BaseModel):
    code: int = Field(..., alias="code")
    session: str = Field(..., alias="session")


def events() -> Type:
    event_types = [
        Message,

        AuthEvent,

        BotOnlineEvent,
        BotOfflineEventActive,
        BotOfflineEventForce,
        BotOfflineEventDropped,
        BotReloginEvent,
        BotGroupPermissionChangeEvent,
        BotMuteEvent,
        BotUnmuteEvent,
        BotJoinGroupEvent,
        BotLeaveEventActive,
        BotLeaveEventKick,
        GroupNameChangeEvent,
        GroupEntranceAnnouncementChangeEvent,
        GroupMuteAllEvent,
        GroupRecallEvent,
        FriendRecallEvent,
        GroupAllowAnonymousChatEvent,
        GroupAllowConfessTalkEvent,
        GroupAllowMemberInviteEvent,
        MemberJoinEvent,
        MemberLeaveEventKick,
        MemberLeaveEventQuit,
        MemberCardChangeEvent,
        MemberSpecialTitleChangeEvent,
        MemberPermissionChangeEvent,
        MemberMuteEvent,
        MemberUnmuteEvent,
        NewFriendRequestEvent,
        MemberJoinRequestEvent,

        BaseEvent
    ]
    return Union[tuple(event_types)]


Events = events()


class WebSocketEvent(BaseModel):
    sync_id: str = Field(..., alias="syncId")
    data: Events
