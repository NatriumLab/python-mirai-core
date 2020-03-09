import asyncio
from typing import DefaultDict, Union, List, Callable, Any, Awaitable
from collections import defaultdict
from dataclasses import dataclass
import signal
from .log import create_logger, install_logger

from .bot import Bot
from .models.events import Event, EventTypes
from .exceptions import SessionException, NetworkException, AuthenticationException, ServerException


@dataclass
class EventHandler:
    func: Callable


class Shutdown(Exception):
    pass


class Updater:
    def __init__(self, bot: Bot, use_websocket: bool = True):
        self.bot = bot
        self.loop = bot.loop
        self.logger = create_logger('Updater')
        self.event_handlers: DefaultDict[EventTypes, List[EventHandler]] = defaultdict(lambda: list())
        self.use_websocket = use_websocket

    async def handshake(self):
        while True:
            try:
                await self.bot.handshake()
                if self.use_websocket:
                    asyncio.run_coroutine_threadsafe(
                        self.bot.create_websocket(self.event_caller, self.handshake), self.loop)
                return
            except NetworkException:
                self.logger.warning('Unable to communicate with Mirai console, retrying in 5 seconds')
                await asyncio.sleep(5)
            except Exception as e:
                self.logger.exception(f'retrying in 5 seconds')
                await asyncio.sleep(5)

    async def run_task(self, shutdown_trigger=None):
        """
        return awaitable coroutine to run in any event loop
        :param shutdown_trigger: shutdown event if running in main thread
        """
        self.logger.debug('Run tasks')
        tasks = [
            self.handshake()
        ]
        if not self.use_websocket:
            tasks.append(self.message_polling())
        if shutdown_trigger:
            tasks.append(self.raise_shutdown(shutdown_trigger))
        await asyncio.wait(tasks)

    def add_handler(self, event: Union[EventTypes, List[EventTypes]]):
        """
        Decorator for event listeners
        Catch all is not supported at this time
        :param event: events.Events
        """
        def receiver_wrapper(func):
            if not asyncio.iscoroutinefunction(func):
                raise TypeError("event body must be a coroutine function.")

            # save function and its parameter types
            event_handler = EventHandler(func)
            if isinstance(event, EventTypes):
                # add listener
                self.event_handlers[event].append(event_handler)
            else:
                for e in event:
                    if isinstance(e, EventTypes):
                        self.event_handlers[e].append(event_handler)
            return func

        return receiver_wrapper

    async def message_polling(self, count=5, interval=0.5):
        """
        polling message and fire events
        :param count: maximum message count for each polling
        :param interval: minimum interval between two polling
        """
        while True:
            await asyncio.sleep(interval)
            try:
                results: List[Event] = await self.bot.fetch_message(count)
                if len(results) > 0:
                    self.logger.debug('Received messages:\n' + '\n'.join([str(result) for result in results]))
                for result in results:
                    asyncio.run_coroutine_threadsafe(self.event_caller(result), self.loop)
            except Exception as e:
                self.logger.warning(f'{e}, new handshake initiated')
                await self.handshake()

    async def event_caller(self, event: Event):
        for handler in self.event_handlers[event.type]:
            if await handler.func(event):  # if the function returns True, stop calling next event
                break

    def run(self, log_to_stderr=True):
        asyncio.set_event_loop(self.loop)

        shutdown_event = asyncio.Event()

        def _signal_handler(*_: Any) -> None:
            shutdown_event.set()

        try:
            self.loop.add_signal_handler(signal.SIGTERM, _signal_handler)
            self.loop.add_signal_handler(signal.SIGINT, _signal_handler)
        except (AttributeError, NotImplementedError):
            pass

        if log_to_stderr:
            install_logger()

        self.loop.create_task(self.run_task(shutdown_trigger=shutdown_event.wait))
        self.loop.run_forever()

    async def raise_shutdown(self, shutdown_event: Callable[..., Awaitable[None]]) -> None:
        await shutdown_event()
        await self.bot.release()
        raise Shutdown()
