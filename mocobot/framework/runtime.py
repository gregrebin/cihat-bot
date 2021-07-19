from mocobot.framework.injector import Injector
from configparser import ConfigParser
from signal import SIGINT, SIGTERM
from typing import Type, Callable, List
import asyncio


def async_run(async_method: Callable):
    def non_async(self, *args, **kwargs):
        asyncio.run(async_method(self, *args, **kwargs))
    return non_async


class Runtime:

    def run(self, args: List[str]):
        pass

    @async_run
    async def _run(self, injector_class: Type[Injector], app_type: Type, app_name: str, config_path: str = None, **arguments):

        configparser = ConfigParser()
        if config_path:
            configparser.read(config_path)

        injector = injector_class(configparser)
        application = injector.inject(app_type, app_name, **arguments)

        loop = asyncio.get_event_loop()
        loop.add_signal_handler(SIGINT, lambda: asyncio.create_task(application.stop()))
        loop.add_signal_handler(SIGTERM, lambda: asyncio.create_task(application.stop()))

        await application.run()
