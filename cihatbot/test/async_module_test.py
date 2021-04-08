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

        self.trader: Trader = Trader()
        self.add_submodule(self.trader)

        self.ui: Ui = Ui()
        self.add_submodule(self.ui)

        # self.trader.connect_module(self.ui)


class App(Module):
    def __init__(self):
        super().__init__({}, __name__)

        self.user: User = User()
        self.add_submodule(self.user)


async def main():

    print("test")
    app = App()

    async def stop(signum, frame):
        await app.stop()

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)

    await app.start()


if __name__ == '__main__':
    asyncio.run(main())
