from cihatbot.module import Module
import asyncio
import signal


class Ui(Module):
    def __init__(self):
        super().__init__({}, __name__)


class Trader(Module):
    def __init__(self):
        super().__init__({}, __name__)


class User(Module):
    def __init__(self):
        super().__init__({}, __name__)

        self.trader: Trader = Trader().init()
        self.add_submodule(self.trader)

        self.ui: Ui = Ui().init()
        self.add_submodule(self.ui)

        # self.trader.connect_module(self.ui)


class App(Module):
    def __init__(self):
        super().__init__({}, __name__)

        self.user: User = User().init()
        self.add_submodule(self.user)


async def main():

    print("test")
    app = App().init()

    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGINT, lambda: asyncio.create_task(app.stop()))
    loop.add_signal_handler(signal.SIGTERM, lambda: asyncio.create_task(app.stop()))

    await app.run()


if __name__ == '__main__':
    asyncio.run(main())
