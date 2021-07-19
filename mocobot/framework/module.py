from __future__ import annotations
from mocobot.framework.logger import Logger
from mocobot.framework.events import Event, EventEmitter, EventListener
from mocobot.framework.scheduler import Scheduler
from mocobot.framework.injector import Injector, InjectorException
from typing import List, Dict, Callable, Type, TypeVar
from configparser import SectionProxy
from abc import ABC, abstractmethod
import functools
import logging
import asyncio


SubModuleType = TypeVar("SubModuleType")


class Module(ABC):

    """
    Part of a program, hierarchically structured, concurrent, listening to each other via events. Has a build in logger.
    Better to be initialized via injector.

    Methods
    -------
    add_submodule(submodule):
        adds new submodule
    emit(event):
        emit event
    log(message):
        log message

    Methods to reimplement
    ----------------------
    pre_run():
        initialization logic
    on_run():
        asynchronous runtime code
    on_event(event):
        event handling logic
    on_stop():
        stop asynchronous runtime code
    post_run():
        termination logic
    """

    def __init__(self, config: SectionProxy, category: Type, name: str) -> None:
        super().__init__()
        self.category = category if isinstance(self, category) else type(self)
        self.name = name
        self.loop = asyncio.get_event_loop()
        self.config: SectionProxy = config
        self.logger: Logger = Logger(self.name, logging.INFO)
        self.emitter: EventEmitter = EventEmitter()
        self.listener: EventListener = EventListener()
        self.scheduler: Scheduler = Scheduler()
        self.injector = Injector({})
        self.submodules: List[Module] = []
        self.is_running: bool = False

    def init(self) -> Module:
        async def listen() -> None:
            await self.listener.listen(self.on_event)
        self.scheduler.schedule(listen())
        self.scheduler.schedule(self.on_run())
        self.post_init()
        return self

    def post_init(self) -> None:
        pass

    def add_submodule(self, submodule: Module) -> None:
        submodule.emitter.add_listener(self.listener)
        self.scheduler.schedule(submodule.run())
        self.submodules.append(submodule)

    def get_category(self, category: Type[SubModuleType]) -> List[SubModuleType]:
        return [submodule for submodule in self.submodules if submodule.category is category]

    def get_submodule(self, category: Type[SubModuleType], **attributes) -> List[SubModuleType]:
        return [submodule
                for submodule
                in self.submodules
                if submodule.category is category
                and functools.reduce(lambda b1, b2: b1 and b2,
                                     (submodule.__getattribute__(k) == v for k, v in attributes.items()),
                                     True)]

    async def run(self) -> None:
        self.log("Start")
        self.pre_run()
        self.is_running = True
        self.log("Running")
        await self.scheduler.run()
        self.log("Stop")
        self.post_run()
        self.log("Finished")

    @abstractmethod
    def pre_run(self) -> None:
        pass

    @abstractmethod
    async def on_run(self) -> None:
        pass

    def on_event(self, event: Event) -> None:
        self.events.get(event.__class__, lambda e: None)(event)

    @property
    @abstractmethod
    def events(self) -> Dict[Type, Callable]:
        pass

    @abstractmethod
    def on_stop(self) -> None:
        pass

    @abstractmethod
    def post_run(self) -> None:
        pass

    def emit(self, event: Event, thread_safe: bool = True) -> None:
        if thread_safe:
            self.loop.call_soon_threadsafe(lambda: self.emitter.emit(event))
        else:
            self.emitter.emit(event)

    def log(self, message: str, level: int = logging.INFO) -> None:
        self.logger.log(
            level, f"""{message} : {asyncio.current_task().get_name()} / {len(asyncio.all_tasks())}"""
        )

    async def stop(self):
        for submodule in self.submodules:
            await submodule.stop()
        await self.listener.stop()
        self.on_stop()
        self.is_running = False

    @staticmethod
    def log_decorator(message):
        def decorator(method):
            def wrapper(self, *args, **kwargs):
                self.log(message)
                method(self, *args, **kwargs)
            return wrapper
        return decorator

