from __future__ import annotations
from cihatbot.events import Event
from cihatbot.module import Module
from typing import Callable, List
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
        super().__init__({})

    def pre_run(self) -> None:
        print("ui pre_run")

    async def on_run(self) -> None:
        print("ui on_run")
        while self.is_running:
            await asyncio.sleep(1)
            self.emit(Event({}))

    def on_event(self, event: Event) -> None:
        print("ui on_event")

    def on_stop(self) -> None:
        print("ui on_stop")

    def post_run(self) -> None:
        print("ui post_run")


class Trader(Module):
    def __init__(self):
        super().__init__({})

    def pre_run(self) -> None:
        print("trader pre_run")

    async def on_run(self) -> None:
        print("trader on_run")

    def on_event(self, event: Event) -> None:
        print("trader on_event")

    def on_stop(self) -> None:
        print("trader on_stop")

    def post_run(self) -> None:
        print("trader post_run")


class User(Module):
    def __init__(self):
        super().__init__({})
        self.uis: List[Ui] = []
        self.traders: List[Trader] = []

    def add_ui(self, ui: Ui):
        self.uis.append(ui)
        self.add_submodule(ui)
        for trader in self.traders:
            ui.connect_module(trader)

    def add_trader(self, trader: Trader):
        self.traders.append(trader)
        self.add_submodule(trader)
        for ui in self.uis:
            trader.connect_module(ui)

    # async def on_run(self) -> None:
    #     print("running user")
    #     count = 0
    #     while self.is_running:
    #         await asyncio.sleep(1)
    #         count += 1
    #         print(f"""{count} seconds passed""""")

    def pre_run(self) -> None:
        print("user pre_run")

    async def on_run(self) -> None:
        print("user on_run")

    def on_event(self, event: Event) -> None:
        print("user on_event")

    def on_stop(self) -> None:
        print("user on_stop")

    def post_run(self) -> None:
        print("user post_run")


class App(Module):
    def __init__(self):
        super().__init__({})
        self.users: List[User] = []

    def pre_run(self) -> None:
        print("app pre_run")

    async def on_run(self) -> None:
        print("app on_run")

    def on_event(self, event: Event) -> None:
        print("app on_event")

    def on_stop(self) -> None:
        print("app on_stop")

    def post_run(self) -> None:
        print("app post_run")

    @inject_user
    def add_user(self, user: User):
        self.users.append(user)
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
    app.users[0].add_ui(Injector.get_ui("ui"))
    app.users[0].add_trader(Injector.get_trader("trader"))

    await app.run()


if __name__ == '__main__':
    asyncio.run(main())
