from typing import List, Dict, Optional
from pydantic import BaseModel

from .base import BaseMessageComponent
from .components import Source


class MessageChain(BaseModel):
    # stores the actual components
    __root__: List[BaseMessageComponent] = []

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
        :param value: dict contains message components
        :return: MessageChain
        """
        from .components import ComponentTypes
        for i in value:
            if not isinstance(i, dict):
                raise TypeError("invaild value")
        return cls(__root__=[ComponentTypes.__members__[m['type']].value(**m) for m in value])

    def __iter__(self):
        yield from self.__root__

    def __getitem__(self, index):
        return self.__root__[index]

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
