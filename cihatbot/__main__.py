from cihatbot.application.injector import Injector
from cihatbot.application.application import Application
from configparser import ConfigParser
from signal import SIGINT, SIGTERM
import asyncio


async def main():
    configparser = ConfigParser()
    configparser.read("cihatbot.local.cfg")

    injector = Injector(configparser)
    application: Application = injector.inject(Application, "test")

    loop = asyncio.get_event_loop()
    loop.add_signal_handler(SIGINT, lambda: asyncio.create_task(application.stop()))
    loop.add_signal_handler(SIGTERM, lambda: asyncio.create_task(application.stop()))

    await application.run()


if __name__ == '__main__':
    asyncio.run(main())

