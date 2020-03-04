import asyncio
from typing import Coroutine, DefaultDict, List
import inspect
from bot import Bot
from collections import defaultdict


class Updater:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.event_listeners: DefaultDict[str, List] = defaultdict(lambda: list())

    async def run_task(self) -> Coroutine:
        pass

    def add_handler(self, event):
        def receiver_wrapper(func):
            if not asyncio.iscoroutinefunction(func):
                raise TypeError("event body must be a coroutine function.")

            self.event_listeners[event].append(func)
            return func

        return receiver_wrapper

    async def message_polling(self):
        pass

    async def event_caller(self, event, context):
        for listener in self.event_listeners[event]:
            translated_mapping = {
                k: annotations_mapping[v](
                    context
                ) \
                for k, v in listener.__annotations__.items() \
                if \
                k != "return" and \
                k not in signature_mapping  # 嗯...你设了什么default? 放你过去.
            }

    @staticmethod
    def signature_getter(func):
        """
        get default argument list from event listener
        :param func:
        :return:
        """
        return {k: v.default for k, v in inspect.signature(func).parameters.items()
                if v.default != inspect._empty}


