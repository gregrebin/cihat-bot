from __future__ import annotations
from cihatbot.framework.module import Module
from cihatbot.application.user import User
from typing import List
from configparser import SectionProxy


class Application(Module):

    log_name = __name__

    def __init__(self, config: SectionProxy) -> None:
        super().__init__(config)
        self.users: List[User] = []

    def add_user(self, user: User) -> User:
        self.users.append(user)
        self.add_submodule(user)
        self.log("Created new user")
        return user
