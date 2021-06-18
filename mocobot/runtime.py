from mocobot.application.injector import Injector
from configparser import ConfigParser
from signal import SIGINT, SIGTERM
from typing import Type, Callable
import asyncio


def async_run(async_method: Callable):
    def non_async(self, *args, **kwargs):
        asyncio.run(async_method(self, *args, **kwargs))
    return non_async


class Runtime:

    def __init__(self, injector_class: Type[Injector], config_path: str):
        self.injector_class = injector_class
        self.config_path = config_path

    @async_run
    async def run(self, app_name: str):

        configparser = ConfigParser()
        configparser.read(self.config_path)

        injector = self.injector_class(configparser)
        application = injector.inject("app", app_name)

        loop = asyncio.get_event_loop()
        loop.add_signal_handler(SIGINT, lambda: asyncio.create_task(application.stop()))
        loop.add_signal_handler(SIGTERM, lambda: asyncio.create_task(application.stop()))

        await application.run()
