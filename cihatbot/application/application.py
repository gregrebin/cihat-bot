from __future__ import annotations
from cihatbot.framework.module import Module
from cihatbot.application.events import Event, AddUserEvent, ConfigEvent
from cihatbot.application.user import User
from typing import List
from configparser import SectionProxy


class Application(Module):

    log_name = __name__

    def __init__(self, config: SectionProxy) -> None:
        super().__init__(config)
        self.users: List[User] = []

    def on_event(self, event: Event) -> None:
        super().on_event(event)

        if event.is_type(AddUserEvent):
            self.add_user(self.injector.inject_user(event.data["user"]))

        if event.is_type(ConfigEvent):
            self.config()

    def add_user(self, user: User) -> None:
        self.users.append(user)
        self.add_submodule(user)
        self.log("Created new user")

    def config(self):
        pass
