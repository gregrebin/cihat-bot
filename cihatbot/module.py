from __future__ import annotations
from cihatbot.logger import Logger
from cihatbot.events import Event, EventEmitter, EventListener
from cihatbot.scheduler import Scheduler
from typing import Dict, Callable, Coroutine, List
from configparser import SectionProxy
import logging


class Module:

    log_name = __name__

    def __init__(self, config: SectionProxy) -> None:
        super().__init__()
        self.config: SectionProxy = config
        self.logger: Logger = Logger(self.log_name, logging.INFO)
        self.emitter: EventEmitter = EventEmitter()
        self.listener: EventListener = EventListener()
        self.scheduler: Scheduler = Scheduler()
        self.injector = Injector()
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

    def connect_module(self, module: Module) -> None:
        module.emitter.add_listener(self.listener)
        self.emitter.add_listener(module.listener)

    async def run(self) -> None:
        self.pre_run()
        self.is_running = True
        await self.scheduler.run()
        self.post_run()

    def pre_run(self) -> None:
        pass

    async def on_run(self) -> None:
        pass

    def on_event(self, event: Event) -> None:
        pass

    def on_stop(self) -> None:
        pass

    def post_run(self) -> None:
        pass

    def emit(self, event: Event) -> None:
        self.emitter.emit(event)

    def log(self, message: str) -> None:
        self.logger.log(logging.INFO, message)

    async def stop(self):
        for submodule in self.submodules:
            await submodule.stop()
        await self.listener.stop()
        self.on_stop()
        self.is_running = False


class Injector:

    def inject_app(self, name: str) -> Module:
        pass

    def inject_user(self, name: str) -> Module:
        pass

    def inject_ui(self, name: str) -> Module:
        pass

    def inject_parser(self, name: str) -> Module:
        pass

    def inject_trader(self, name: str) -> Module:
        pass

    def inject_connector(self, name: str) -> Module:
        pass
