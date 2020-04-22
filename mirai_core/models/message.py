from enum import Enum
from pydantic import BaseModel
from abc import abstractmethod
from enum import Enum
from typing import List, Dict, Optional, overload, Iterable, Union
from pydantic import Field, validator, HttpUrl, BaseModel
from pydantic.generics import GenericModel
from pathlib import Path
import datetime
from collections import MutableSequence

__all__ = [
    "MessageComponentTypes",
    "BaseMessageComponent",
    'Plain',
    'Source',
    'At',
    'AtAll',
    'Face',
    'Image',
    'Unknown',
    'Quote',
    'ComponentTypes',
    'LocalImage',
    'MessageChain',
    'qq_emoji_text_list'
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


# original text copied from Tim
qq_emoji_text_list = {
    0:   '[惊讶]',
    1:   '[撇嘴]',
    2:   '[色]',
    3:   '[发呆]',
    4:   '[得意]',
    5:   '[流泪]',
    6:   '[害羞]',
    7:   '[闭嘴]',
    8:   '[睡]',
    9:   '[大哭]',
    10:  '[尴尬]',
    11:  '[发怒]',
    12:  '[调皮]',
    13:  '[呲牙]',
    14:  '[微笑]',
    15:  '[难过]',
    16:  '[酷]',
    17:  '[Empty]',
    18:  '[抓狂]',
    19:  '[吐]',
    20:  '[偷笑]',
    21:  '[可爱]',
    22:  '[白眼]',
    23:  '[傲慢]',
    24:  '[饥饿]',
    25:  '[困]',
    26:  '[惊恐]',
    27:  '[流汗]',
    28:  '[憨笑]',
    29:  '[悠闲]',
    30:  '[奋斗]',
    31:  '[咒骂]',
    32:  '[疑问]',
    33:  '[嘘]',
    34:  '[晕]',
    35:  '[折磨]',
    36:  '[衰]',
    37:  '[骷髅]',
    38:  '[敲打]',
    39:  '[再见]',
    40:  '[Empty]',
    41:  '[发抖]',
    42:  '[爱情]',
    43:  '[跳跳]',
    44:  '[Empty]',
    45:  '[Empty]',
    46:  '[猪头]',
    47:  '[Empty]',
    48:  '[Empty]',
    49:  '[拥抱]',
    50:  '[Empty]',
    51:  '[Empty]',
    52:  '[Empty]',
    53:  '[蛋糕]',
    54:  '[闪电]',
    55:  '[炸弹]',
    56:  '[刀]',
    57:  '[足球]',
    58:  '[Empty]',
    59:  '[便便]',
    60:  '[咖啡]',
    61:  '[饭]',
    62:  '[Empty]',
    63:  '[玫瑰]',
    64:  '[凋谢]',
    65:  '[Empty]',
    66:  '[爱心]',
    67:  '[心碎]',
    68:  '[Empty]',
    69:  '[礼物]',
    70:  '[Empty]',
    71:  '[Empty]',
    72:  '[Empty]',
    73:  '[Empty]',
    74:  '[太阳]',
    75:  '[月亮]',
    76:  '[赞]',
    77:  '[踩]',
    78:  '[握手]',
    79:  '[胜利]',
    80:  '[Empty]',
    81:  '[Empty]',
    82:  '[Empty]',
    83:  '[Empty]',
    84:  '[Empty]',
    85:  '[飞吻]',
    86:  '[怄火]',
    87:  '[Empty]',
    88:  '[Empty]',
    89:  '[西瓜]',
    90:  '[Empty]',
    91:  '[Empty]',
    92:  '[Empty]',
    93:  '[Empty]',
    94:  '[Empty]',
    95:  '[Empty]',
    96:  '[冷汗]',
    97:  '[擦汗]',
    98:  '[抠鼻]',
    99:  '[鼓掌]',
    100: '[糗大了]',
    101: '[坏笑]',
    102: '[左哼哼]',
    103: '[右哼哼]',
    104: '[哈欠]',
    105: '[鄙视]',
    106: '[委屈]',
    107: '[快哭了]',
    108: '[阴险]',
    109: '[亲亲]',
    110: '[吓]',
    111: '[可怜]',
    112: '[菜刀]',
    113: '[啤酒]',
    114: '[篮球]',
    115: '[乒乓]',
    116: '[示爱]',
    117: '[瓢虫]',
    118: '[抱拳]',
    119: '[勾引]',
    120: '[拳头]',
    121: '[差劲]',
    122: '[爱你]',
    123: '[NO]',
    124: '[OK]',
    125: '[转圈]',
    126: '[磕头]',
    127: '[回头]',
    128: '[跳绳]',
    129: '[挥手]',
    130: '[激动]',
    131: '[街舞]',
    132: '[献吻]',
    133: '[左太极]',
    134: '[右太极]',
    135: '[Empty]',
    136: '[双喜]',
    137: '[鞭炮]',
    138: '[灯笼]',
    139: '[发财]',
    140: '[K歌]',
    141: '[购物]',
    142: '[邮件]',
    143: '[帅]',
    144: '[喝彩]',
    145: '[祈祷]',
    146: '[爆筋]',
    147: '[棒棒糖]',
    148: '[喝奶]',
    149: '[下面]',
    150: '[香蕉]',
    151: '[飞机]',
    152: '[开车]',
    153: '[高铁左车头]',
    154: '[车厢]',
    155: '[高铁右车头]',
    156: '[多云]',
    157: '[下雨]',
    158: '[钞票]',
    159: '[熊猫]',
    160: '[灯泡]',
    161: '[风车]',
    162: '[闹钟]',
    163: '[打伞]',
    164: '[彩球]',
    165: '[钻戒]',
    166: '[沙发]',
    167: '[纸巾]',
    168: '[药]',
    169: '[手枪]',
    170: '[青蛙]',
    171: '[茶]',
    172: '[眨眼睛]',
    173: '[泪奔]',
    174: '[无奈]',
    175: '[卖萌]',
    176: '[小纠结]',
    177: '[喷血]',
    178: '[斜眼笑]',
    179: '[doge]',
    180: '[惊喜]',
    181: '[骚扰]',
    182: '[笑哭]',
    183: '[我最美]',
    184: '[河蟹]',
    185: '[羊驼]',
    186: '[Empty]',
    187: '[幽灵]',
    188: '[蛋]',
    189: '[Empty]',
    190: '[菊花]',
    191: '[Empty]',
    192: '[红包]',
    193: '[大笑]',
    194: '[不开心]',
    195: '[Empty]',
    196: '[Empty]',
    197: '[冷漠]',
    198: '[呃]',
    199: '[好棒]',
    200: '[拜托]',
    201: '[点赞]',
    202: '[无聊]',
    203: '[托脸]',
    204: '[吃]',
    205: '[送花]',
    206: '[害怕]',
    207: '[花痴]',
    208: '[小样儿]',
    209: '[Empty]',
    210: '[飙泪]',
    211: '[我不看]',
    212: '[托腮]',
    213: '[Empty]',
    214: '[啵啵]',
    215: '[糊脸]',
    216: '[拍头]',
    217: '[扯一扯]',
    218: '[舔一舔]',
    219: '[蹭一蹭]',
    220: '[拽炸天]',
    221: '[顶呱呱]',
    222: '[抱抱]',
    223: '[暴击]',
    224: '[开枪]',
    225: '[撩一撩]',
    226: '[拍桌]',
    227: '[拍手]',
    228: '[恭喜]',
    229: '[干杯]',
    230: '[嘲讽]',
    231: '[哼]',
    232: '[佛系]',
    233: '[掐一掐]',
    234: '[惊呆]',
    235: '[颤抖]',
    236: '[啃头]',
    237: '[偷看]',
    238: '[扇脸]',
    239: '[原谅]',
    240: '[喷脸]',
    241: '[生日快乐]',
    242: '[Empty]',
    243: '[Empty]',
    244: '[Empty]',
    245: '[Empty]',
    246: '[Empty]',
    247: '[Empty]',
    248: '[Empty]',
    249: '[Empty]',
    250: '[Empty]',
    251: '[Empty]',
    252: '[Empty]',
    253: '[Empty]',
    254: '[Empty]',
    255: '[Empty]',
}


class MessageChain(BaseModel, MutableSequence):
    # stores the actual components
    __root__: List[BaseMessageComponent] = []

    def insert(self, index: int, object) -> None:
        self.__root__.insert(index, object)

    @overload
    @abstractmethod
    def __setitem__(self, i: int, o) -> None:
        ...

    @overload
    @abstractmethod
    def __setitem__(self, s: slice, o: Iterable) -> None:
        ...

    def __setitem__(self, i: int, o) -> None:
        self.__root__.__setitem__(i, o)

    @overload
    @abstractmethod
    def __delitem__(self, i: int) -> None:
        ...

    @overload
    @abstractmethod
    def __delitem__(self, i: slice) -> None:
        ...

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

    @classmethod
    def custom_parse(cls, value: List[Dict]) -> 'MessageChain':
        """
        construct message chain from dict
        used only when receiving messages from mirai

        :param value: dict contains message components
        :return: MessageChain
        """
        for i in value:
            if not isinstance(i, dict):
                raise TypeError("invaild value")
        return cls(__root__=[ComponentTypes.__members__[m['type']].value(**m) for m in value])

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

    def get_source(self) -> 'Source':
        result = self.get_first(Source)
        assert isinstance(result, Source)
        return result

    def get_quote(self) -> 'Quote':
        result = self.get_first(Quote)
        if result:
            assert isinstance(result, Quote)
            return result


class Source(BaseMessageComponent):
    """
    The source of the message
    Not a valid component for outbound message
    """
    type = MessageComponentTypes.Source
    id: int  # the message id: higher 32 bits are sequence id, and lower 32 bits are random id
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
    type = MessageComponentTypes.Plain
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


class Quote(BaseMessageComponent):
    """
    Quote component
    Not a valid component for outbound message
    """
    type = MessageComponentTypes.Quote
    id: int  # origin message id
    groupId: int  # origin group id
    senderId: int  # origin sender id
    origin: MessageChain  # origin message (Source and other content without Quote)

    def __str__(self):
        return ''

    def __repr__(self):
        return f'[Quote: id={self.id}]'


class At(GenericModel, BaseMessageComponent):
    """
    At component
    Available for outbound message
    """
    type = MessageComponentTypes.At
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
    type = MessageComponentTypes.AtAll

    def __str__(self):
        return '@All'

    def __repr__(self):
        return f'[AtAll]'


class Face(BaseMessageComponent):
    """
    Face component
    Available for outbound message
    """
    type = MessageComponentTypes.Face
    faceId: int  # face id, see qq_emoji_text_list for details

    def __init__(self, faceId, **kwargs):
        """
        Construct Face component

        :param face_id: unsigned 8-bit face id
        """
        super().__init__(faceId=faceId, **kwargs)

    def __str__(self):
        return qq_emoji_text_list[self.faceId]

    def __repr__(self):
        return f'[Face: id={self.faceId}, {qq_emoji_text_list[self.faceId]}]'


class Image(BaseMessageComponent):
    """
    Received image component
    Available for outbound message
    """
    type = MessageComponentTypes.Image
    imageId: str
    url: Optional[HttpUrl] = None

    def __init__(self, imageId, **kwargs):
        """
        Construct Image from mirai styled uuid

        :param imageId: uuid as str (see https://github.com/mamoe/mirai-api-http/blob/master/MessageType.md#image)
        """
        super().__init__(imageId=imageId, **kwargs)

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


class LocalImage:
    """
    Local image component
    Available for outbound message
    """
    path: Path  # absolute path to image

    def __init__(self, path=None):
        """
        Construct LocalImage component

        :param path: absolute path on disk
        """
        if isinstance(path, str):
            self.path = Path(path)
        elif isinstance(path, Path):
            self.path = path


class Xml(BaseMessageComponent):
    """
    Xml component
    Available for outbound message
    """
    type = MessageComponentTypes.Xml
    XML: str  # xml content

    def __init__(self, XML: str, **kwargs):
        """
        Construct Xml component

        :param xml: str contains xml
        """
        super().__init__(XML=XML, **kwargs)


class Json(BaseMessageComponent):
    """
    Json component
    Available for outbound message
    """
    type = MessageComponentTypes.Json
    Json: dict = Field(..., alias="json")  # json content

    def __init__(self, Json: Union[dict, List], **kwargs):
        """
        Construct Json component

        :param json: json content
        """
        super().__init__(Json=Json, **kwargs)


class App(BaseMessageComponent):
    """
    App component
    Available for outbound message
    """
    type = MessageComponentTypes.App
    content: str  # app content

    def __init__(self, content: str, **kwargs):
        """
        Construct App component

        :param content: app content
        """
        super().__init__(content=content, **kwargs)


class Unknown(BaseMessageComponent):
    """
    Unknown component
    Not a valid component for outbound message
    """
    type = MessageComponentTypes.Unknown
    text: str  # content in string

    def __str__(self):
        return ''

    def __repr__(self):
        return '[Unknown]'


class ComponentTypes(Enum):
    Plain = Plain
    Source = Source
    At = At
    AtAll = AtAll
    Face = Face
    Image = Image
    Quote = Quote
    Xml = Xml
    Json = Json
    App = App
    Unknown = Unknown


MessageComponents = {
    'At':      At,
    'AtAll':   AtAll,
    'Face':    Face,
    'Plain':   Plain,
    'Image':   Image,
    'Source':  Source,
    'Quote':   Quote,
    'Xml':     Xml,
    'Json':    Json,
    'App':     App,
    'Unknown': Unknown
}


class BotMessage(BaseModel):
    type: str = 'BotMessage'
    messageId: int


class ImageType(Enum):
    Friend = 'friend'
    Group = 'group'
