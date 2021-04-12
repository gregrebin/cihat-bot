from __future__ import annotations
from cihatbot.module import Module
from typing import Callable
import asyncio
import signal


def inject_app(func: Callable[[Module, App], None]) -> Callable[[Module, str], None]:
    def wrapped(self, name):
        injected = Injector.get_app(name)
        return func(self, injected)
    return wrapped


def inject_user(func: Callable[[Module, User], None]) -> Callable[[Module, str], None]:
    def wrapped(self, name):
        injected = Injector.get_user(name)
        return func(self, injected)
    return wrapped


def inject_trader(func: Callable[[Module, Trader], None]) -> Callable[[Module, str], None]:
    def wrapped(self, name):
        injected = Injector.get_trader(name)
        return func(self, injected)
    return wrapped


def inject_ui(func: Callable[[Module, Ui], None]) -> Callable[[Module, str], None]:
    def wrapped(self, name):
        injected = Injector.get_ui(name)
        return func(self, injected)
    return wrapped


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

    @inject_user
    def add_user(self, user: User):
        self.add_submodule(user)


class Injector:

    apps = {
        "app": App
    }
    users = {
        "user": User
    }
    traders = {
        "trader": Trader
    }
    uis = {
        "ui": Ui
    }

    @staticmethod
    def get_app(name):
        return Injector.apps[name]().init()

    @staticmethod
    def get_user(name):
        return Injector.users[name]().init()

    @staticmethod
    def get_trader(name):
        return Injector.traders[name]().init()

    @staticmethod
    def get_ui(name):
        return Injector.uis[name]().init()


async def main():

    print("test")
    app = Injector.get_app("app")

    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGINT, lambda: asyncio.create_task(app.stop()))
    loop.add_signal_handler(signal.SIGTERM, lambda: asyncio.create_task(app.stop()))

    app.add_user("user")
    await app.run()


if __name__ == '__main__':
    asyncio.run(main())
