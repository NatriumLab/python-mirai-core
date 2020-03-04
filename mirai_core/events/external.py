from enum import Enum
from pydantic import BaseModel
from models import Permission, Group, Member, Friend
import typing as T


class ExternalEventTypes(Enum):
    # Bot events
    BotOnlineEvent = "BotOnlineEvent"
    BotOfflineEventActive = "BotOfflineEventActive"
    BotOfflineEventForce = "BotOfflineEventForce"
    BotOfflineEventDropped = "BotOfflineEventDropped"
    BotReloginEvent = "BotReloginEvent"
    BotGroupPermissionChangeEvent = "BotGroupPermissionChangeEvent"
    BotMuteEvent = "BotMuteEvent"
    BotUnmuteEvent = "BotUnmuteEvent"
    BotJoinGroupEvent = "BotJoinGroupEvent"

    # Group events
    GroupNameChangeEvent = "GroupNameChangeEvent"
    GroupEntranceAnnouncementChangeEvent = "GroupEntranceAnnouncementChangeEvent"
    GroupMuteAllEvent = "GroupMuteAllEvent"

    # Group permission events
    GroupAllowAnonymousChatEvent = "GroupAllowAnonymousChatEvent"  # 群设置 是否允许匿名聊天 被修改
    GroupAllowConfessTalkEvent = "GroupAllowConfessTalkEvent"  # 坦白说
    GroupAllowMemberInviteEvent = "GroupAllowMemberInviteEvent"  # 邀请进群

    # Group member events
    MemberJoinEvent = "MemberJoinEvent"
    MemberLeaveEventKick = "MemberLeaveEventKick"
    MemberLeaveEventQuit = "MemberLeaveEventQuit"
    MemberCardChangeEvent = "MemberCardChangeEvent"
    MemberSpecialTitleChangeEvent = "MemberSpecialTitleChangeEvent"
    MemberPermissionChangeEvent = "MemberPermissionChangeEvent"
    MemberMuteEvent = "MemberMuteEvent"
    MemberUnmuteEvent = "MemberUnmuteEvent"

    # python mirai core exception
    # ExceptionEvent = "ExceptionEvent"


class ExternalEvent(BaseModel):
    type: ExternalEventTypes


class BotOnlineEvent(ExternalEvent):
    type = ExternalEventTypes.BotOnlineEvent
    qq: int


class BotOfflineEventActive(ExternalEvent):
    type = ExternalEventTypes.BotOfflineEventActive
    qq: int


class BotOfflineEventForce(ExternalEvent):
    type = ExternalEventTypes.BotOfflineEventForce
    qq: int


class BotOfflineEventDropped(ExternalEvent):
    type = ExternalEventTypes.BotOfflineEventDropped
    qq: int


class BotReloginEvent(ExternalEvent):
    type = ExternalEventTypes.BotReloginEvent
    qq: int


class BotGroupPermissionChangeEvent(ExternalEvent):
    type = ExternalEventTypes.BotGroupPermissionChangeEvent
    origin: Permission
    new: Permission
    group: Group


class BotMuteEvent(ExternalEvent):
    type = ExternalEventTypes.BotMuteEvent
    durationSeconds: int
    operator: T.Optional[Member]


class BotUnmuteEvent(ExternalEvent):
    type = ExternalEventTypes.BotUnmuteEvent
    operator: T.Optional[Member]


class BotJoinGroupEvent(ExternalEvent):
    type = ExternalEventTypes.BotJoinGroupEvent
    group: Group


class GroupNameChangeEvent(ExternalEvent):
    type = ExternalEventTypes.GroupNameChangeEvent
    origin: str
    new: str
    group: Group
    isByBot: bool


class GroupEntranceAnnouncementChangeEvent(ExternalEvent):
    type = ExternalEventTypes.GroupEntranceAnnouncementChangeEvent
    origin: str
    new: str
    group: Group
    operator: T.Optional[Member]


class GroupMuteAllEvent(ExternalEvent):
    type = ExternalEventTypes.GroupMuteAllEvent
    origin: bool
    new: bool
    group: Group
    operator: T.Optional[Member]


class GroupAllowAnonymousChatEvent(ExternalEvent):
    type = ExternalEventTypes.GroupAllowAnonymousChatEvent
    origin: bool
    new: bool
    group: Group
    operator: T.Optional[Member]


class GroupAllowConfessTalkEvent(ExternalEvent):
    type = ExternalEventTypes.GroupAllowAnonymousChatEvent
    origin: bool
    new: bool
    group: Group
    isByBot: bool


class GroupAllowMemberInviteEvent(ExternalEvent):
    type = ExternalEventTypes.GroupAllowMemberInviteEvent
    origin: bool
    new: bool
    group: Group
    operator: T.Optional[Member]


class MemberJoinEvent(ExternalEvent):
    type = ExternalEventTypes.MemberJoinEvent
    member: Member


class MemberLeaveEventKick(ExternalEvent):
    type = ExternalEventTypes.MemberLeaveEventKick
    member: Member
    operator: T.Optional[Member]


class MemberLeaveEventQuit(ExternalEvent):
    type = ExternalEventTypes.MemberLeaveEventQuit
    member: Member


class MemberCardChangeEvent(ExternalEvent):
    type = ExternalEventTypes.MemberCardChangeEvent
    origin: str
    new: str
    member: Member
    operator: T.Optional[Member]


class MemberSpecialTitleChangeEvent(ExternalEvent):
    type = ExternalEventTypes.MemberSpecialTitleChangeEvent
    origin: str
    new: str
    member: Member


class MemberPermissionChangeEvent(ExternalEvent):
    type = ExternalEventTypes.MemberPermissionChangeEvent
    origin: str
    new: str
    member: Member


class MemberMuteEvent(ExternalEvent):
    type = ExternalEventTypes.MemberMuteEvent
    durationSeconds: int
    member: Member
    operator: T.Optional[Member]


class MemberUnmuteEvent(ExternalEvent):
    type = ExternalEventTypes.MemberUnmuteEvent
    member: Member
    operator: T.Optional[Member]


class ExternalEvents(Enum):
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
