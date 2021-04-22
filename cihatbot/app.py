from __future__ import annotations
from cihatbot.module import Module
from cihatbot.user import User
from cihatbot.events import Event, EventListener, AddUserEvent
from typing import Dict, List
from configparser import SectionProxy
import logging


class Application(Module):

    log_name = __name__

    def __init__(self, config: SectionProxy) -> None:
        super().__init__(config)
        self.log("Initializing Cihat-bot")
        self.users: List[User] = []
        self.log("Initialization complete")

    def add_user(self, user: User) -> User:
        self.users.append(user)
        self.add_submodule(user)
        self.logger.log(logging.INFO, "Created new user")
        return user

    def on_event(self, event: Event) -> None:
        if event.is_type(AddUserEvent):
            self.add_user(self.injector.inject_user("user"))
