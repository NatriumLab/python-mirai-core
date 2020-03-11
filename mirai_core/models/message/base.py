from enum import Enum
from pydantic import BaseModel

__all__ = [
    "MessageComponentTypes",
    "BaseMessageComponent"
]


class MessageComponentTypes(Enum):
    Source = "Source"
    Plain = "Plain"
    Face = "Face"
    At = "At"
    AtAll = "AtAll"
    Image = "Image"
    Quote = "Quote"
    Xml = "Xml"
    Json = "Json"
    App = "App"
    Unknown = "Unknown"


class BaseMessageComponent(BaseModel):
    type: MessageComponentTypes

    def __str__(self):
        """
        for plain text extraction
        :return: human readable text component
        """
        return ''
