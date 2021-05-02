from __future__ import annotations
from cihatbot.module import Module
from cihatbot.application.user import User
from cihatbot.events import Event
from cihatbot.application.events import AddUserEvent
from typing import List
from configparser import SectionProxy
import logging


class Application(Module):

    log_name = __name__

    def __init__(self, config: SectionProxy) -> None:
        super().__init__(config)
        self.users: List[User] = []

    def add_user(self, user: User) -> User:
        self.users.append(user)
        self.add_submodule(user)
        self.logger.log(logging.INFO, "Created new user")
        return user
