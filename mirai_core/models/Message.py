from abc import abstractmethod
from enum import Enum
from typing import List, Dict, Optional, overload, Iterable, Union, Literal, Type, Any
from pydantic import Field, validator, HttpUrl, BaseModel, Extra, root_validator
from .Constant import qq_emoji_text_list
import datetime
from collections import MutableSequence
import json

__all__ = [
    "BaseMessageComponent",
    'Plain',
    'Source',
    'At',
    'AtAll',
    'Face',
    'Image',
    'FlashImage',
    'Quote',
    'App',
    'Json',
    'Xml',
    'Poke',
    'MessageChain',
    'BotMessage'
]


class BaseMessageComponent(BaseModel):
    type: str

    class Config:
        extra = Extra.allow

    def __str__(self):
        """
        for plain text extraction
        :return: human readable text component
        """
        return 'Unknown message component: ' + json.dumps(self.dict(), ensure_ascii=False, indent=4)

    def __repr__(self):
        return '[Unknown]'


class Source(BaseMessageComponent):
    """
    The source of the message
    Not a valid component for outbound message
    """
    type: Literal['Source'] = 'Source'
    id: int  # the sequence id
    time: datetime.datetime  # the timestamp the message was sent

    def __str__(self):
        return ''

    def __repr__(self):
        return f'[Source: id={self.id}, time={self.time}]'


class Plain(BaseMessageComponent):
    """
    Text component
    Available for outbound message
    """
    type: Literal['Plain'] = 'Plain'
    text: str  # text content

    def __init__(self, text: str, **kwargs):
        """
        Construct text component

        :param text: message text
        """
        super().__init__(text=text, **kwargs)

    def __str__(self):
        return self.text

    def __repr__(self):
        return f'[Plain: {self.text}]'


class At(BaseMessageComponent):
    """
    At component
    Available for outbound message
    """
    type: Literal['At'] = 'At'
    target: int  # target qq number
    display: str  # display name (only used for inbound at), '@' already included

    def __init__(self, target, **kwargs):
        """
        Construct at component

        :param target: target qq number
        """
        super().__init__(target=target, **kwargs)

    def __str__(self):
        return self.display

    def __repr__(self):
        return f'[At: target={self.target}, display={self.display}]'


class AtAll(BaseMessageComponent):
    """
    AtAll component
    Available for outbound message
    """
    type: Literal['AtAll'] = 'AtAll'

    def __str__(self):
        return '@All'

    def __repr__(self):
        return f'[AtAll]'


class Face(BaseMessageComponent):
    """
    Face component
    Available for outbound message
    """
    type: Literal['Face'] = 'Face'
    faceId: int  # face id, see qq_emoji_text_list for details

    def __init__(self, faceId, **kwargs):
        """
        Construct Face component

        :param face_id: unsigned integer face id
        """
        super().__init__(faceId=faceId, **kwargs)

    def __str__(self):
        return qq_emoji_text_list[self.faceId] if self.faceId in qq_emoji_text_list else "[Unknown]"

    def __repr__(self):
        face_text = qq_emoji_text_list[self.faceId] if self.faceId in qq_emoji_text_list else "[Unknown]"
        return f'[Face: id={self.faceId}, {face_text}]'


class Image(BaseMessageComponent):
    """
    Received image component
    Available for outbound message
    """
    type: Literal['Image'] = 'Image'
    imageId: Optional[str]
    url: Optional[HttpUrl]
    path: Optional[str]

    def __init__(self,
                 imageId: Optional[str] = None,
                 url: Optional[HttpUrl] = None,
                 path: Optional[str] = None,
                 **kwargs):
        """
        Construct Image from mirai styled uuid, http url or local file path

        :param imageId: uuid as str (see https://github.com/mamoe/mirai-api-http/blob/master/MessageType.md#image)
        :param url: image url (http url)
        :param path: local image path (absolute path or relative path under "plugins/MiraiAPIHTTP/images")
        """
        super().__init__(imageId=imageId, url=url, path=path, **kwargs)

    def __str__(self):
        return ''

    def __repr__(self):
        return f'[Image: {self.imageId}]'

    @property
    def image_type(self):
        """
        get image type from pattern

        :return: 'friend' or 'group', if uuid is invalid format, return 'unknown'
        """
        if self.imageId.startswith('/'):
            return 'friend'
        elif self.imageId.startswith('{'):
            return 'group'
        else:
            'unknown'


class FlashImage(BaseMessageComponent):
    """
    Received image component
    Available for outbound message
    """
    type: Literal['FlashImage'] = 'FlashImage'
    imageId: Optional[str]
    url: Optional[HttpUrl]
    path: Optional[str]

    def __init__(self,
                 imageId: Optional[str] = None,
                 url: Optional[HttpUrl] = None,
                 path: Optional[str] = None,
                 **kwargs):
        """
        Construct Image from mirai styled uuid, http url or local file path

        :param imageId: uuid as str (see https://github.com/mamoe/mirai-api-http/blob/master/MessageType.md#image)
        :param url: image url (http url)
        :param path: local image path (absolute path or relative path under "plugins/MiraiAPIHTTP/images")
        """
        super().__init__(imageId=imageId, url=url, path=path, **kwargs)

    def __str__(self):
        return ''

    def __repr__(self):
        return f'[Image: {self.imageId}]'

    @property
    def image_type(self):
        """
        get image type from pattern

        :return: 'friend' or 'group', if uuid is invalid format, return 'unknown'
        """
        if self.imageId.startswith('/'):
            return 'friend'
        elif self.imageId.startswith('{'):
            return 'group'
        else:
            'unknown'


class Xml(BaseMessageComponent):
    """
    Xml component
    Available for outbound message
    """
    type: Literal['Xml'] = 'Xml'
    xml: str  # xml content

    def __init__(self, xml: str, **kwargs):
        """
        Construct Xml component

        :param xml: str contains xml
        """
        super().__init__(xml=xml, **kwargs)

    def __str__(self):
        return self.xml

    def __repr__(self):
        return f'[Xml: {self.xml}]'


class Json(BaseMessageComponent):
    """
    Json component
    Available for outbound message
    """
    type: Literal['Json'] = 'Json'
    Json: str = Field(..., alias="json")  # json content

    def __init__(self, Json: str, **kwargs):
        """
        Construct Json component

        :param json: json content
        """
        super().__init__(Json=Json, **kwargs)

    def __str__(self):
        return self.json

    def __repr__(self):
        return f'[Json: {self.json}]'


class App(BaseMessageComponent):
    """
    App component
    Available for outbound message
    """
    type: Literal['App'] = 'App'
    content: str  # app content

    def __init__(self, content: str, **kwargs):
        """
        Construct App component

        :param content: app content
        """
        super().__init__(content=content, **kwargs)

    def __str__(self):
        return str(self.content)

    def __repr__(self):
        return f'[App: {str(self.content)}]'


class PokeChoices(str, Enum):
    Poke = 'Poke'
    ShowLove = 'ShowLove'
    Like = 'Like'
    Heartbroken = 'Heartbroken'
    SixSixSix = 'SixSixSix'
    FangDaZhao = 'FangDaZhao'


class Poke(BaseMessageComponent):
    """
    Poke component
    Available for outbound message
    """
    type: Literal['Poke'] = 'Poke'
    name: PokeChoices

    def __init__(self, name: PokeChoices, **kwargs):
        """
        Construct Poke component

        :param name: Poke content
        """
        super().__init__(name=name, **kwargs)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'[Poke: {self.name}]'


class QuoteMessageChain(BaseModel):
    # stores the actual components
    __root__: List[Union[Source, Plain, Image, At, Face, FlashImage, AtAll, Xml, Json, App, Poke, BaseMessageComponent]]

    def insert(self, index: int, object) -> None:
        self.__root__.insert(index, object)

    def __setitem__(self, i: int, o) -> None:
        self.__root__.__setitem__(i, o)

    def __delitem__(self, i: int) -> None:
        self.__root__.__delitem__(i)

    def __add__(self, value):
        # merge two message chain or append one component
        if isinstance(value, BaseMessageComponent):
            self.__root__.append(value)
            return self
        elif isinstance(value, MessageChain):
            self.__root__ += value.__root__
            return self

    def __str__(self) -> str:
        return ''.join([str(i) for i in self.__root__])

    def __iter__(self):
        return self.__root__.__iter__()

    def __getitem__(self, index):
        return self.__root__.__getitem__(index)

    def has(self, component_class) -> bool:
        """
        test if any item in MessageChain is component_class

        :param component_class: the class for the component
        :return: boolean
        """
        for i in self:
            if isinstance(i, component_class):
                return True
        else:
            return False

    def __len__(self) -> int:
        return len(self.__root__)

    def get_first(self, component_class) -> Optional[BaseMessageComponent]:
        """
        Get the first component with component_class

        :param component_class: the class for the component
        :return: None or the component
        """
        for i in self.__root__:
            if isinstance(i, component_class):
                return i

    def get_all(self, component_class) -> List[BaseMessageComponent]:
        return [i for i in self.__root__ if isinstance(i, component_class)]

    def get_source(self) -> Source:
        result = self.get_first(Source)
        assert isinstance(result, Source)
        return result


class Quote(BaseMessageComponent):
    """
    Quote component
    Not a valid component for outbound message
    """
    type: Literal['Quote'] = 'Quote'
    id: int  # origin message id
    groupId: int  # origin group id
    senderId: int  # origin sender id
    targetId: int  # group id
    origin: QuoteMessageChain  # origin message (Source and other content without Quote)

    def __init__(self, origin=None, **kwargs):
        origin = QuoteMessageChain.parse_obj(origin)
        super().__init__(origin=origin, **kwargs)

    def __str__(self):
        return ''

    def __repr__(self):
        return f'[Quote: id={self.id}]'


class MessageChain(BaseModel):
    # stores the actual components
    __root__: List[
        Union[Source, Plain, Image, Quote, At, Face, FlashImage, AtAll, Xml, Json, App, Poke, BaseMessageComponent]]

    def insert(self, index: int, object) -> None:
        self.__root__.insert(index, object)

    def __setitem__(self, i: int, o) -> None:
        self.__root__.__setitem__(i, o)

    def __delitem__(self, i: int) -> None:
        self.__root__.__delitem__(i)

    def __add__(self, value):
        # merge two message chain or append one component
        if isinstance(value, BaseMessageComponent):
            self.__root__.append(value)
            return self
        elif isinstance(value, MessageChain):
            self.__root__ += value.__root__
            return self

    def __str__(self) -> str:
        return ''.join([str(i) for i in self.__root__])

    def __iter__(self):
        return self.__root__.__iter__()

    def __getitem__(self, index):
        return self.__root__.__getitem__(index)

    def has(self, component_class) -> bool:
        """
        test if any item in MessageChain is component_class

        :param component_class: the class for the component
        :return: boolean
        """
        for i in self:
            if isinstance(i, component_class):
                return True
        else:
            return False

    def __len__(self) -> int:
        return len(self.__root__)

    def get_first(self, component_class) -> Optional[BaseMessageComponent]:
        """
        Get the first component with component_class

        :param component_class: the class for the component
        :return: None or the component
        """
        for i in self.__root__:
            if isinstance(i, component_class):
                return i

    def get_all(self, component_class) -> List[BaseMessageComponent]:
        return [i for i in self.__root__ if isinstance(i, component_class)]

    def get_source(self) -> Source:
        result = self.get_first(Source)
        assert isinstance(result, Source)
        return result

    def get_quote(self) -> Quote:
        result = self.get_first(Quote)
        if result:
            assert isinstance(result, Quote)
            return result


class BotMessage(BaseModel):
    type: str = 'BotMessage'
    messageId: int
