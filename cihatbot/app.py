from cihatbot.logger import Logger
from cihatbot.events import Event, UI_EVENTS, TRADER_EVENTS
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
from queue import Queue
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
        self._init_default_user()

        self.logger.log(logging.INFO, "Initialization complete")

    def _init_default_user(self):

        user = User(self.all_events, self.config, self.exit_event, self.logger)
        user.add_trader(self.config["all"]["trader"], self.config["all"]["connector"])
        user.add_ui(self.config["all"]["ui"], self.config["all"]["parser"])
        self.users.append(user)

    def run(self):

        self.logger.log(logging.INFO, "Cihat-bot started")

        for user in self.users:
            user.start()

        while not self.exit_event.isSet():
            event = self.all_events.get()
            self.receive_event(event)

        for user in self.users:
            user.join()

        self.logger.log(logging.INFO, "Cihat-bot stopped")

    def receive_event(self, event: Event):

        if event.name == "NEW_USER":
            self.add_user()

    def add_user(self):

        user = User(self.all_events, self.config, self.exit_event, self.logger)
        self.users.append(user)

    def exit(self, signum, frame):

        self.exit_event.set()


class User(Thread):

    def __init__(self, app_all_events: Queue, config: ConfigParser, exit_event: ThreadEvent, logger: Logger) -> None:
        super().__init__()

        self.uis: List[Ui] = []
        self.traders: List[Trader] = []

        self.ui_events: Queue = Queue()
        self.trader_events: Queue = Queue()
        self.all_events: Queue = Queue()
        self.app_all_events: Queue = app_all_events

        self.config: ConfigParser = config
        self.exit_event: ThreadEvent = exit_event
        self.logger: Logger = logger

    def add_ui(self, ui_name: str, parser_name: str) -> Ui:

        ui_class = UIS[ui_name]
        parser_class = PARSERS[parser_name]

        parser = parser_class()
        ui = ui_class(self.config[ui_name], self.trader_events, self.exit_event, parser)

        ui.on_event(self.ui_event_handler)
        self.uis.append(ui)
        return ui

    def add_trader(self, trader_name: str, connector_name: str) -> Trader:

        trader_class = TRADERS[trader_name]
        connector_class = CONNECTORS[connector_name]

        connector = connector_class()
        trader = trader_class(self.config[trader_name], self.ui_events, self.exit_event, connector)

        trader.on_event(self.trader_event_handler)
        self.traders.append(trader)
        return trader

    def ui_event_handler(self, event: Event) -> None:

        self.logger.log(logging.INFO, f"""New ui event: {event}""")
        self.ui_events.put(event)
        self.all_events.put(event)
        self.app_all_events.put(event)

    def trader_event_handler(self, event: Event) -> None:

        self.logger.log(logging.INFO, f"""New trader event: {event}""")
        self.trader_events.put(event)
        self.all_events.put(event)
        self.app_all_events.put(event)

    def receive_event(self, event: Event) -> None:

        if event.name == "ADD_TRADER":
            trader = self.add_trader(event.data["trader_name"], event.data["connector_name"])
            trader.start()

        elif event.name == "ADD_UI":
            ui = self.add_ui(event.data["ui_name"], event.data["parser_name"])
            ui.start()

    def run(self):

        for ui in self.uis:
            ui.start()
        for trader in self.traders:
            trader.start()

        while not self.exit_event.isSet():
            event = self.all_events.get()
            self.receive_event(event)

        for ui in self.uis:
            ui.join()
        for trader in self.traders:
            trader.join()
