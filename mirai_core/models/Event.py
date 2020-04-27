from enum import Enum
from pydantic import BaseModel, Field
from .Entity import Permission, Group, Member, Friend
from .Message import MessageChain
from typing import Optional
from datetime import datetime


class EventTypes(Enum):
    """
    EventTypes is used for registering handlers
    """
    # Bot events
    BotOnlineEvent = 'BotOnlineEvent'
    BotOfflineEventActive = 'BotOfflineEventActive'
    BotOfflineEventForce = 'BotOfflineEventForce'
    BotOfflineEventDropped = 'BotOfflineEventDropped'
    BotReloginEvent = 'BotReloginEvent'
    BotGroupPermissionChangeEvent = 'BotGroupPermissionChangeEvent'
    BotMuteEvent = 'BotMuteEvent'
    BotUnmuteEvent = 'BotUnmuteEvent'
    BotJoinGroupEvent = 'BotJoinGroupEvent'

    # Group events
    GroupNameChangeEvent = 'GroupNameChangeEvent'
    GroupEntranceAnnouncementChangeEvent = 'GroupEntranceAnnouncementChangeEvent'
    GroupMuteAllEvent = 'GroupMuteAllEvent'
    GroupRecallEvent = "GroupRecallEvent"
    FriendRecallEvent = "FriendRecallEvent"

    # Group permission events
    GroupAllowAnonymousChatEvent = 'GroupAllowAnonymousChatEvent'  # 群设置 是否允许匿名聊天 被修改
    GroupAllowConfessTalkEvent = 'GroupAllowConfessTalkEvent'  # 坦白说
    GroupAllowMemberInviteEvent = 'GroupAllowMemberInviteEvent'  # 邀请进群

    # Group member events
    MemberJoinEvent = 'MemberJoinEvent'
    MemberLeaveEventKick = 'MemberLeaveEventKick'
    MemberLeaveEventQuit = 'MemberLeaveEventQuit'
    MemberCardChangeEvent = 'MemberCardChangeEvent'
    MemberSpecialTitleChangeEvent = 'MemberSpecialTitleChangeEvent'
    MemberPermissionChangeEvent = 'MemberPermissionChangeEvent'
    MemberMuteEvent = 'MemberMuteEvent'
    MemberUnmuteEvent = 'MemberUnmuteEvent'

    # Requests
    NewFriendRequestEvent = "NewFriendRequestEvent"
    MemberJoinRequestEvent = "MemberJoinRequestEvent"

    # Message events
    FriendMessage = 'FriendMessage'
    GroupMessage = 'GroupMessage'


class NewFriendRequestResponse(Enum):
    ACCEPT = 0
    REFUSE = 1
    REFUSE_AND_BLACKLIST = 2


class MemberJoinRequestResponse(Enum):
    ACCEPT = 0
    REFUSE = 1
    IGNORE = 2
    REFUSE_AND_BLACKLIST = 3
    IGNORE_AND_BLACKLIST = 4


class Event(BaseModel):
    type: EventTypes


class BotOnlineEvent(Event):
    type = EventTypes.BotOnlineEvent
    qq: int

    def __str__(self):
        return f'[{self.type.value}: qq={self.qq}]'


class BotOfflineEventActive(Event):
    type = EventTypes.BotOfflineEventActive
    qq: int

    def __str__(self):
        return f'[{self.type.value}: qq={self.qq}]'


class BotOfflineEventForce(Event):
    type = EventTypes.BotOfflineEventForce
    qq: int

    def __str__(self):
        return f'[{self.type.value}: qq={self.qq}]'


class BotOfflineEventDropped(Event):
    type = EventTypes.BotOfflineEventDropped
    qq: int

    def __str__(self):
        return f'[{self.type.value}: qq={self.qq}]'


class BotReloginEvent(Event):
    type = EventTypes.BotReloginEvent
    qq: int

    def __str__(self):
        return f'[{self.type.value}: qq={self.qq}]'


class BotGroupPermissionChangeEvent(Event):
    type = EventTypes.BotGroupPermissionChangeEvent
    origin: Permission
    current: Permission
    group: Group

    def __str__(self):
        return f'[{self.type.value}: ' \
               f'origin={repr(self.origin)}, new={repr(self.current)}, group={repr(self.group)}]'


class BotMuteEvent(Event):
    type = EventTypes.BotMuteEvent
    durationSeconds: int
    operator: Optional[Member]

    def __str__(self):
        return f'[{self.type.value}: durationSeconds={self.durationSeconds}, operator={repr(self.operator)}]'


class BotUnmuteEvent(Event):
    type = EventTypes.BotUnmuteEvent
    operator: Optional[Member]

    def __str__(self):
        return f'[{self.type.value}: operator={repr(self.operator)}]'


class BotJoinGroupEvent(Event):
    type = EventTypes.BotJoinGroupEvent
    group: Group

    def __str__(self):
        return f'[{self.type.value}: group={repr(self.group)}]'


class GroupRecallEvent(Event):
    type: EventTypes = EventTypes.GroupRecallEvent
    authorId: int
    messageId: int
    time: datetime
    group: Group
    operator: Optional[Member]


class FriendRecallEvent(Event):
    type: EventTypes = EventTypes.FriendRecallEvent
    authorId: int
    messageId: int
    time: int
    operator: int


class GroupNameChangeEvent(Event):
    type = EventTypes.GroupNameChangeEvent
    origin: str
    current: str
    group: Group
    isByBot: bool

    def __str__(self):
        return f'[{self.type.value}: ' \
               f'origin={self.origin}, new={self.current}, group={repr(self.group)}, isByBot={self.isByBot}]'


class GroupEntranceAnnouncementChangeEvent(Event):
    type = EventTypes.GroupEntranceAnnouncementChangeEvent
    origin: str
    current: str
    group: Group
    operator: Optional[Member]

    def __str__(self):
        return f'[{self.type.value}: ' \
               f'origin={self.origin}, new={self.current}, group={repr(self.group)}, operator={repr(self.operator)}]'


class GroupMuteAllEvent(Event):
    type = EventTypes.GroupMuteAllEvent
    origin: bool
    current: bool
    group: Group
    operator: Optional[Member]

    def __str__(self):
        return f'[{self.type.value}: ' \
               f'origin={self.origin}, new={self.current}, group={repr(self.group)}, operator={repr(self.operator)}]'


class GroupAllowAnonymousChatEvent(Event):
    type = EventTypes.GroupAllowAnonymousChatEvent
    origin: bool
    current: bool
    group: Group
    operator: Optional[Member]

    def __str__(self):
        return f'[{self.type.value}: ' \
               f'origin={self.origin}, new={self.current}, group={repr(self.group)}, operator={repr(self.operator)}]'


class GroupAllowConfessTalkEvent(Event):
    type = EventTypes.GroupAllowAnonymousChatEvent
    origin: bool
    current: bool
    group: Group
    isByBot: bool

    def __str__(self):
        return f'[{self.type.value}: ' \
               f'origin={self.origin}, new={self.current}, group={repr(self.group)}, isByBot={self.isByBot}]'


class GroupAllowMemberInviteEvent(Event):
    type = EventTypes.GroupAllowMemberInviteEvent
    origin: bool
    current: bool
    group: Group
    operator: Optional[Member]

    def __str__(self):
        return f'[{self.type.value}: ' \
               f'origin={self.origin}, new={self.current}, group={repr(self.group)}, operator={repr(self.operator)}]'


class MemberJoinEvent(Event):
    type = EventTypes.MemberJoinEvent
    member: Member

    def __str__(self):
        return f'[{self.type.value}: ' \
               f'member={repr(self.member)}]'


class MemberLeaveEventKick(Event):
    type = EventTypes.MemberLeaveEventKick
    member: Member
    operator: Optional[Member]

    def __str__(self):
        return f'[{self.type.value}: ' \
               f'member={repr(self.member)}, operator={repr(self.operator)}]'


class MemberLeaveEventQuit(Event):
    type = EventTypes.MemberLeaveEventQuit
    member: Member

    def __str__(self):
        return f'[{self.type.value}: ' \
               f'member={repr(self.member)}]'


class MemberCardChangeEvent(Event):
    type = EventTypes.MemberCardChangeEvent
    origin: str
    current: str
    member: Member
    operator: Optional[Member]

    def __str__(self):
        return f'[{self.type.value}: ' \
               f'origin={self.origin}, new={self.current}, member={repr(self.member)}, operator={repr(self.operator)}]'


class MemberSpecialTitleChangeEvent(Event):
    type = EventTypes.MemberSpecialTitleChangeEvent
    origin: str
    current: str
    member: Member

    def __str__(self):
        return f'[{self.type.value}: ' \
               f'origin={self.origin}, new={self.current}, member={repr(self.member)}]'


class MemberPermissionChangeEvent(Event):
    type = EventTypes.MemberPermissionChangeEvent
    origin: str
    current: str
    member: Member

    def __str__(self):
        return f'[{self.type.value}: ' \
               f'origin={self.origin}, new={self.current}, member={repr(self.member)}]'


class MemberMuteEvent(Event):
    type = EventTypes.MemberMuteEvent
    durationSeconds: int
    member: Member
    operator: Optional[Member]

    def __str__(self):
        return f'[{self.type.value}: ' \
               f'durationSeconds={self.durationSeconds}, member={repr(self.member)}, operator={repr(self.operator)}]'


class MemberUnmuteEvent(Event):
    type = EventTypes.MemberUnmuteEvent
    member: Member
    operator: Optional[Member]

    def __str__(self):
        return f'[{self.type.value}: ' \
               f'member={repr(self.member)}, operator={repr(self.operator)}]'


class FriendMessage(Event):
    type: EventTypes = EventTypes.FriendMessage
    messageChain: Optional[MessageChain]
    sender: Friend

    def __str__(self):
        return f'[{self.type.value}: ' \
               f'messageChain={str(self.messageChain)}, sender={repr(self.sender)}]'


class GroupMessage(Event):
    type: EventTypes = EventTypes.GroupMessage
    messageChain: Optional[MessageChain]
    sender: Member

    def __str__(self):
        return f'[{self.type.value}: ' \
               f'messageChain={str(self.messageChain)}, sender={repr(self.sender)}]'


class NewFriendRequestEvent(Event):
    type: EventTypes = EventTypes.NewFriendRequestEvent
    requestId: int = Field(..., alias="eventId")
    supplicant: int = Field(..., alias="fromId")  # 即请求方 QQ
    sourceGroup: Optional[int] = Field(..., alias="groupId")
    nickname: str = Field(..., alias="nick")


class MemberJoinRequestEvent(Event):
    type: EventTypes = EventTypes.MemberJoinRequestEvent
    requestId: int = Field(..., alias="eventId")
    supplicant: int = Field(..., alias="fromId")  # 即请求方 QQ
    sourceGroup: Optional[int] = Field(..., alias="groupId")
    groupName: str = Field(..., alias="groupName")
    nickname: str = Field(..., alias="nick")


class Events(Enum):
    """
    Internal use only
    """
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
    GroupRecallEvent = GroupRecallEvent
    FriendRecallEvent = FriendRecallEvent

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

    # Join
    NewFriendRequestEvent = NewFriendRequestEvent
    MemberJoinRequestEvent = MemberJoinRequestEvent

    FriendMessage = FriendMessage
    GroupMessage = GroupMessage
