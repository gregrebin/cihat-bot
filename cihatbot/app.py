from __future__ import annotations
from cihatbot.module import Module
from cihatbot.user import User
from cihatbot.logger import Logger
from cihatbot.events import Event, EventListener, AddUserEvent
from cihatbot.scheduler import Scheduler
from configparser import ConfigParser
from typing import Dict, List
from signal import signal, SIGINT, SIGTERM
import logging


class Application(Module):

    def __init__(self, config: Dict) -> None:
        super().__init__(config, __name__)

        self.log("Initializing Cihat-bot")

        signal(SIGINT, self.exit)
        signal(SIGTERM, self.exit)

        self.users: List[User] = []

        self.log("Initialization complete")

    def add_user(self, ui_name: str = None, parser_name: str = None, trader_name: str = None, connector_name: str = None, ui_config: Dict = None, trader_config: Dict = None) -> User:

        if not ui_name:
            ui_name = self.config["ui"]
        if not parser_name:
            parser_name = self.config["parser"]
        if not trader_name:
            trader_name = self.config["trader"]
        if not connector_name:
            connector_name = self.config["connector"]

        user = User(self.listener, self.config)
        user.add_ui(ui_name, parser_name, ui_config)
        user.add_trader(trader_name, connector_name, trader_config)

        self.users.append(user)
        self.scheduler.schedule(user)

        self.logger.log(logging.INFO, "Created new user")
        return user

    def run(self) -> None:

        self.logger.log(logging.INFO, "Starting cihat-bot")
        self.scheduler.run()
        self.logger.log(logging.INFO, "Cihat-bot started")

        self.listener.listen(self.on_event)

        self.logger.log(logging.INFO, "Stopping cihat-bot")
        self.scheduler.stop()
        self.logger.log(logging.INFO, "Cihat-bot stopped")

    def on_event(self, event: Event) -> None:

        if event.is_type(AddUserEvent):
            self.add_user(event.data["ui"], event.data["parser"], event.data["trader"], event.data["connector"], event.data["ui_config"], event.data["trader_config"])

    def exit(self, signum, frame):

        for user in self.users:
            user.stop()
        self.stop()
