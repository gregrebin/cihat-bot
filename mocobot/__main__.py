from mocobot.runtime import Runtime
from mocobot.application.injector import Injector
from mocobot.application.application import Application
from configparser import ConfigParser
from signal import SIGINT, SIGTERM
import asyncio


# async def main():
#     configparser = ConfigParser()
#     configparser.read("mocobot.local.cfg")
#
#     injector = Injector(configparser)
#     application = injector.inject(Application, "test_app")
#
#     loop = asyncio.get_event_loop()
#     loop.add_signal_handler(SIGINT, lambda: asyncio.create_task(application.stop()))
#     loop.add_signal_handler(SIGTERM, lambda: asyncio.create_task(application.stop()))
#
#     await application.run()


if __name__ == '__main__':
    # asyncio.run(main())
    runtime = Runtime(Injector, "mocobot.local.cfg")
    runtime.run("test_app")

