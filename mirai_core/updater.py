import asyncio
from typing import DefaultDict, Union, List, Callable, Any, Awaitable
from collections import defaultdict
from dataclasses import dataclass
import signal
from .log import create_logger, install_logger
from .bot import Bot
from .models.Event import BaseEvent, Events
from .exceptions import SessionException, NetworkException, AuthenticationException, ServerException


class Updater:
    def __init__(self, bot: Bot, use_websocket: bool = True):
        """
        Initialize Updater

        :param bot: the Bot object to use
        :param use_websocket: bool. whether websocket (recommended) should be used
        """
        self.bot = bot
        self.loop = bot.loop
        self.logger = create_logger('Updater')
        self.event_handlers: DefaultDict[Events, List[EventHandler]] = defaultdict(lambda: list())
        self.use_websocket = use_websocket

    async def run_task(self, shutdown_hook: callable = None):
        """
        return awaitable coroutine to run in event loop (must be the same loop as bot object)

        :param shutdown_hook: callable, if running in main thread, this must be set. Trigger is called on shutdown
        """
        self.logger.debug('Run tasks')
        tasks = [
            self.handshake()
        ]
        if not self.use_websocket:
            tasks.append(self.message_polling())
        if shutdown_hook:
            tasks.append(self.raise_shutdown(shutdown_hook))
        await asyncio.wait(tasks)

    def add_handler(self, event: Union[Events, List[Events]]):
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
            nonlocal event
            if not isinstance(event, list):
                event = [event]
            for e in event:
                if e in Events.__args__:
                    if e.__name__ == 'Message':
                        self.event_handlers['GroupMessage'].append(event_handler)
                        self.event_handlers['FriendMessage'].append(event_handler)
                        self.event_handlers['TempMessage'].append(event_handler)
                    else:
                        self.event_handlers[e.__name__].append(event_handler)
            return func

        return receiver_wrapper

    def run(self, log_to_stderr=True) -> None:
        """
        Start the Updater and block the thread

        :param log_to_stderr: if you are setting other loggers that capture the log from this Library, set to False
        """
        asyncio.set_event_loop(self.loop)
        self.loop.set_exception_handler(self.handle_exception)

        shutdown_event = asyncio.Event()

        def _signal_handler(*_: Any) -> None:
            shutdown_event.set()

        try:
            self.loop.add_signal_handler(signal.SIGTERM, _signal_handler)
            self.loop.add_signal_handler(signal.SIGINT, _signal_handler)
        except (AttributeError, NotImplementedError, RuntimeError):
            pass

        if log_to_stderr:
            install_logger()

        self.loop.create_task(self.run_task(shutdown_hook=shutdown_event.wait))
        self.loop.run_forever()

    async def handshake(self):
        """
        Internal use only, automatic handshake
        Called when launch or websocket disconnects

        :return:
        """
        while True:
            try:
                await self.bot.handshake()
                if self.use_websocket:
                    asyncio.run_coroutine_threadsafe(
                        self.bot.create_websocket(self.event_caller, self.handshake), self.loop)
                return True
            except NetworkException:
                self.logger.warning('Unable to communicate with Mirai console, retrying in 5 seconds')
            except Exception as e:
                self.logger.exception(f'retrying in 5 seconds')
            await asyncio.sleep(5)

    async def message_polling(self, count=5, interval=0.5) -> None:
        """
        Internal use only, polling message and fire events

        :param count: maximum message count for each polling
        :param interval: minimum interval between two polling
        """
        while True:
            await asyncio.sleep(interval)
            try:
                results: List[BaseEvent] = await self.bot.fetch_message(count)
                if len(results) > 0:
                    self.logger.debug('Received messages:\n' + '\n'.join([str(result) for result in results]))
                for result in results:
                    asyncio.run_coroutine_threadsafe(self.event_caller(result), self.loop)
            except Exception as e:
                self.logger.warning(f'{e}, new handshake initiated')
                await self.handshake()

    async def event_caller(self, event: BaseEvent) -> None:
        """
        Internal use only, call the event handlers sequentially

        :param event: the event
        """
        for handler in self.event_handlers[event.type]:
            if await handler.func(event):  # if the function returns True, stop calling next event
                break

    async def raise_shutdown(self, shutdown_event: Callable[..., Awaitable[None]]) -> None:
        """
        Internal use only, shutdown

        :param shutdown_event: callable
        """
        await shutdown_event()
        await self.bot.release()
        raise Shutdown()

    def handle_exception(self, loop, context):
        # context["message"] will always be there; but context["exception"] may not
        msg = context.get("exception", context["message"])
        self.logger.exception('Unhandled exception: ', exc_info=msg)


@dataclass
class EventHandler:
    """
    Contains the callback function
    """
    func: Callable


class Shutdown(Exception):
    """
    Internal use only
    Shutdown BaseEvent
    """
    pass
