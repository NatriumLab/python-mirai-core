from enum import Enum
from pydantic import BaseModel


class BotMessage(BaseModel):
    type: str = 'BotMessage'
    messageId: int


class ImageType(Enum):
    Friend = "friend"
    Group = "group"
