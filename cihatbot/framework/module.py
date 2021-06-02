from __future__ import annotations
from cihatbot.framework.logger import Logger
from cihatbot.framework.events import Event, EventEmitter, EventListener
from cihatbot.framework.scheduler import Scheduler
from cihatbot.framework.injector import Injector
from typing import List
from configparser import SectionProxy
import logging
import asyncio


class Module:

    """
    Part of a program, hierarchically structured, concurrent, listening to each other via events. Has a build in logger.

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

    log_name = __name__

    def __init__(self, config: SectionProxy) -> None:
        super().__init__()
        self.loop = asyncio.get_event_loop()
        self.config: SectionProxy = config
        self.logger: Logger = Logger(self.log_name, logging.INFO)
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
        return self

    def add_submodule(self, submodule: Module) -> None:
        submodule.emitter.add_listener(self.listener)
        self.scheduler.schedule(submodule.run())
        self.submodules.append(submodule)

    async def run(self) -> None:
        self.pre_run()
        self.is_running = True
        await self.scheduler.run()
        self.post_run()

    def pre_run(self) -> None:
        self.log("pre_run")

    async def on_run(self) -> None:
        self.log("on_run")

    def on_event(self, event: Event) -> None:
        self.log(f"""on_event: {event}""")

    def on_stop(self) -> None:
        self.log("on_stop")

    def post_run(self) -> None:
        self.log("post_run")

    def emit(self, event: Event, thread_safe: bool = True) -> None:
        # self.log(f"""emit: {event}""")
        if thread_safe:
            self.loop.call_soon_threadsafe(lambda: self.emitter.emit(event))
        else:
            self.emitter.emit(event)

    def log(self, message: str) -> None:
        self.logger.log(logging.INFO, message)

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

