from cihatbot.application.injector import Injector
from configparser import ConfigParser
from signal import SIGINT, SIGTERM
import asyncio


async def main():
    configparser = ConfigParser()
    configparser.read("cihatbot.local.cfg")

    injector = Injector(configparser)
    application = injector.inject_app("app")

    loop = asyncio.get_event_loop()
    loop.add_signal_handler(SIGINT, lambda: asyncio.create_task(application.stop()))
    loop.add_signal_handler(SIGTERM, lambda: asyncio.create_task(application.stop()))

    await application.run()


if __name__ == '__main__':
    asyncio.run(main())

