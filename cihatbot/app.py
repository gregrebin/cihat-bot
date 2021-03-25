from __future__ import annotations
from cihatbot.logger import Logger
from cihatbot.events import Event, UI_EVENTS, TRADER_EVENTS, USER_EVENTS, APP_EVENTS
from cihatbot.ui.ui import Ui
from cihatbot.ui.telegram import Telegram
from cihatbot.parser.parser import Parser
from cihatbot.parser.complete_parser import CompleteParser
from cihatbot.parser.simple_parser import SimpleParser
from cihatbot.trader.trader import Trader
from cihatbot.trader.real import RealTrader
from cihatbot.connector.connector import Connector
from cihatbot.connector.binance import BinanceConnector
from configparser import ConfigParser, SectionProxy
from queue import Queue, Empty
from threading import Thread, Event as ThreadEvent
from typing import Type, Dict, List
from signal import signal, SIGINT, SIGTERM
import logging


""" Concrete ui implementation classes """
UIS: Dict[str, Type[Ui]] = {
    "telegram-ui": Telegram
}

PARSERS: Dict[str, Type[Parser]] = {
    "complete-parser": CompleteParser,
    "simple-parser": SimpleParser
}

""" Concrete trader implementation classes """
TRADERS: Dict[str, Type[Trader]] = {
    "real-trader": RealTrader
}

CONNECTORS: Dict[str, Type[Connector]] = {
    "binance-connector": BinanceConnector
}


class Application:

    def __init__(self, config_file: str) -> None:

        self.logger: Logger = Logger(__name__, logging.INFO)
        self.logger.log(logging.INFO, "Initializing Cihat-bot")

        self.exit_event: ThreadEvent = ThreadEvent()
        signal(SIGINT, self.exit)
        signal(SIGTERM, self.exit)

        self.config: ConfigParser = ConfigParser()
        self.config.read(config_file)

        self.all_events: Queue = Queue()
        self.users: List[User] = []

        self.logger.log(logging.INFO, "Initialization complete")

    def run(self):

        self.logger.log(logging.INFO, "Starting cihat-bot")

        self.add_user(
            self.config["app"]["ui"], self.config["app"]["parser"],
            self.config["app"]["trader"], self.config["app"]["connector"]
        )

        self.logger.log(logging.INFO, "Cihat-bot started")

        while not self.exit_event.isSet():
            try:
                event = self.all_events.get(block=False)
                self.receive_event(event)
            except Empty:
                pass

        self.logger.log(logging.INFO, "Stopping cihat-bot")

        for user in self.users:
            user.join()

        self.logger.log(logging.INFO, "Cihat-bot stopped")

    def receive_event(self, event: Event):

        if event.name == "NEW_USER":
            self.add_user(event.data["ui"], event.data["parser"], event.data["trader"], event.data["connector"])

    def add_user(self, ui_name: str, parser_name: str, trader_name: str, connector_name: str):

        self._init_user(ui_name, parser_name, trader_name, connector_name).start()
        self.logger.log(logging.INFO, f"""Started new user""")

    def _init_user(self, ui_name: str, parser_name: str, trader_name: str, connector_name: str) -> User:

        user = User(self.all_events, self.config, self.exit_event, self.logger)
        user.add_ui(ui_name, parser_name)
        user.add_trader(trader_name, connector_name)
        self.users.append(user)
        self.logger.log(logging.INFO, "Created new user")

        return user

    def exit(self, signum, frame):

        self.exit_event.set()


class User(Thread):

    def __init__(self, app_events: Queue, config: ConfigParser, exit_event: ThreadEvent, logger: Logger) -> None:
        super().__init__()

        self.uis: List[Ui] = []
        self.traders: List[Trader] = []

        self.ui_events: Queue = Queue()
        self.trader_events: Queue = Queue()
        self.user_events: Queue = Queue()
        self.app_events: Queue = app_events

        self.config: ConfigParser = config
        self.exit_event: ThreadEvent = exit_event
        self.logger: Logger = logger

        self.logger.log(logging.INFO, f"""New user initialized""")

    def add_ui(self, ui_name: str, parser_name: str) -> Ui:

        ui_class = UIS[ui_name]
        parser_class = PARSERS[parser_name]

        parser = parser_class()
        ui = ui_class(self.config[ui_name], self.trader_events, self.exit_event, parser)

        ui.on_event(self.ui_event_handler)
        self.uis.append(ui)

        self.logger.log(logging.INFO, f"""Added {ui_name} with {parser_name}""")
        return ui

    def add_trader(self, trader_name: str, connector_name: str) -> Trader:

        trader_class = TRADERS[trader_name]
        connector_class = CONNECTORS[connector_name]

        connector = connector_class()
        trader = trader_class(self.config[trader_name], self.ui_events, self.exit_event, connector)

        trader.on_event(self.trader_event_handler)
        self.traders.append(trader)

        self.logger.log(logging.INFO, f"""Added {trader_name} with {connector_name}""")
        return trader

    def ui_event_handler(self, event: Event) -> None:

        self.logger.log(logging.INFO, f"""New ui event: {event.name}""")

        if event.name in UI_EVENTS:
            self.ui_events.put(event)
        elif event.name in USER_EVENTS:
            self.user_events.put(event)
        elif event.name in APP_EVENTS:
            self.app_events.put(event)

    def trader_event_handler(self, event: Event) -> None:

        self.logger.log(logging.INFO, f"""New trader event: {event.name}""")

        if event.name in TRADER_EVENTS:
            self.trader_events.put(event)
        elif event.name in USER_EVENTS:
            self.user_events.put(event)
        elif event.name in APP_EVENTS:
            self.app_events.put(event)

    def run(self):

        for ui in self.uis:
            ui.start()
        for trader in self.traders:
            trader.start()

        while not self.exit_event.isSet():
            try:
                event = self.user_events.get(block=False)
                self.receive_event(event)
            except Empty:
                pass

        for ui in self.uis:
            ui.join()
        for trader in self.traders:
            trader.join()

    def receive_event(self, event: Event) -> None:

        if event.name == "ADD_TRADER":
            self.add_trader(event.data["trader_name"], event.data["connector_name"]).start()

        elif event.name == "ADD_UI":
            self.add_ui(event.data["ui_name"], event.data["parser_name"]).start()
