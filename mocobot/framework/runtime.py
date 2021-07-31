from mocobot.framework.module import Module
from configparser import ConfigParser
from signal import SIGINT, SIGTERM
from typing import Type, Callable, List
import asyncio


def async_run(async_method: Callable):
    def non_async(self, *args, **kwargs):
        asyncio.run(async_method(self, *args, **kwargs))
    return non_async


class Runtime:

    async def start(self, args: List[str]):
        pass

    async def run(self, module: Module):
        loop = asyncio.get_event_loop()
        loop.add_signal_handler(SIGINT, lambda: asyncio.create_task(module.stop()))
        loop.add_signal_handler(SIGTERM, lambda: asyncio.create_task(module.stop()))
        await module.run()
