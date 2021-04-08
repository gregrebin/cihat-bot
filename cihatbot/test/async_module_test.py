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

    def pre_run(self) -> None:
        print("creating user")

    async def in_run(self) -> None:
        count = 0
        while self.is_running:
            await asyncio.sleep(1)
            count += 1
            print(f"""{count} seconds passed""""")

    def post_run(self) -> None:
        print("deleting user")


class App(Module):
    def __init__(self):
        super().__init__({}, __name__)

        self.user1: User = User().init()
        self.user2: User = User().init()
        self.add_submodule(self.user1)
        self.add_submodule(self.user2)


async def main():

    print("test")
    app = App().init()

    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGINT, lambda: asyncio.create_task(app.stop()))
    loop.add_signal_handler(signal.SIGTERM, lambda: asyncio.create_task(app.stop()))

    await app.run()


if __name__ == '__main__':
    asyncio.run(main())
