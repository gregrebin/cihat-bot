from __future__ import annotations
from cihatbot.logger import Logger
from cihatbot.events import Event, EventEmitter, EventListener
from cihatbot.scheduler import Scheduler
from typing import Dict, Callable, Coroutine, List
import logging


class Module:

    def __init__(self, config: Dict, logger_name: str) -> None:
        super().__init__()
        self.config: Dict = config
        self.logger: Logger = Logger(logger_name, logging.INFO)
        self.emitter: EventEmitter = EventEmitter()
        self.listener: EventListener = EventListener()
        self.scheduler: Scheduler = Scheduler()
        self.submodules: List[Module] = []

    def add_submodule(self, submodule: Module):
        submodule.emitter.add_listener(self.listener)
        self.scheduler.schedule(submodule.start)

    async def start(self) -> None:

        async def listen() -> None:
            await self.listener.listen(self.on_event)

        self.scheduler.schedule(listen)
        self.scheduler.start()
        await self.scheduler.wait()

    def on_event(self, event: Event) -> None:
        pass

    def emit(self, event: Event) -> None:
        self.emitter.emit(event)

    def log(self, message: str) -> None:
        self.logger.log(logging.INFO, message)

    async def stop(self):
        for submodule in self.submodules:
            await submodule.stop()
        await self.listener.stop()
