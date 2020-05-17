from enum import Enum


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


class MessageType(str, Enum):
    GROUP = 'GroupMessage'
    FRIEND = 'FriendMessage'
    TEMP = 'TempMessage'

    @property
    def chat_type(self):
        return {
            'GroupMessage':  'group',
            'FriendMessage': 'friend',
            'TempMessage':   'temp'
        }[self]
