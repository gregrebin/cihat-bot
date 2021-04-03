from __future__ import annotations
from cihatbot.user import User
from cihatbot.logger import Logger
from cihatbot.events import Event, EventListener
from configparser import ConfigParser
from typing import Dict, List
from signal import signal, SIGINT, SIGTERM
import logging


class Application:

    def __init__(self, config_file: str) -> None:

        self.logger: Logger = Logger(__name__, logging.INFO)
        self.logger.log(logging.INFO, "Initializing Cihat-bot")

        signal(SIGINT, self.exit)
        signal(SIGTERM, self.exit)

        self.config: ConfigParser = ConfigParser()
        self.config.read(config_file)

        self.listener: EventListener = EventListener()
        self.users: List[User] = []

        self.logger.log(logging.INFO, "Initialization complete")

    def add_user(self, ui_name: str = None, parser_name: str = None, trader_name: str = None, connector_name: str = None, ui_config: Dict = None, trader_config: Dict = None) -> User:

        if not ui_name:
            ui_name = self.config["app"]["ui"]
        if not parser_name:
            parser_name = self.config["app"]["parser"]
        if not trader_name:
            trader_name = self.config["app"]["trader"]
        if not connector_name:
            connector_name = self.config["app"]["connector"]

        user = User(self.listener, self.config)
        user.add_ui(ui_name, parser_name, ui_config)
        user.add_trader(trader_name, connector_name, trader_config)
        self.users.append(user)

        self.logger.log(logging.INFO, "Created new user")
        return user

    def run(self) -> None:

        self.logger.log(logging.INFO, "Starting cihat-bot")

        for user in self.users:
            user.start()

        self.logger.log(logging.INFO, "Cihat-bot started")

        self.listener.listen(self.on_event)

        self.logger.log(logging.INFO, "Stopping cihat-bot")

        for user in self.users:
            user.join()

        self.logger.log(logging.INFO, "Cihat-bot stopped")

    def on_event(self, event: Event) -> None:

        if event.name == "NEW_USER":
            self.add_user(event.data["ui"], event.data["parser"], event.data["trader"], event.data["connector"]).start()

    def exit(self, signum, frame):

        for user in self.users:
            user.stop()
        self.listener.stop()
