from typing import Optional
from enum import Enum
from models import Friend, Group, Member
from pydantic import BaseModel
from .chain import MessageChain


class MessageItemType(Enum):
    FriendMessage = "FriendMessage"
    GroupMessage = "GroupMessage"
    BotMessage = "BotMessage"


class FriendMessage(BaseModel):
    type: MessageItemType = "FriendMessage"
    messageChain: Optional[MessageChain]
    sender: Friend


class GroupMessage(BaseModel):
    type: MessageItemType = "GroupMessage"
    messageChain: Optional[MessageChain]
    sender: Member


class BotMessage(BaseModel):
    type: MessageItemType = 'BotMessage'
    messageId: int


MessageTypes = {
    "GroupMessage":  GroupMessage,
    "FriendMessage": FriendMessage
}
