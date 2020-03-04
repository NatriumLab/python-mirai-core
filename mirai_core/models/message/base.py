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
    Unknown = "Unknown"

class BaseMessageComponent(BaseModel):
    type: MessageComponentTypes

    def display(self):
        """
        for debugging purpose
        :return: detailed string
        """
        return self.__repr__()

    def __str__(self):
        """
        for plain text extraction
        :return: human readable text component
        """
        return ''
