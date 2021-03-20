from cihatbot.events import Event, UI_EVENTS, TRADER_EVENTS
from cihatbot.ui.ui import Ui
from cihatbot.ui.cli import Cli
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
from threading import Event as ThreadEvent
from typing import Type, Dict
from signal import signal, SIGINT, SIGTERM


""" Concrete ui implementation classes """
UIS: Dict[str, Type[Ui]] = {
    "cli-ui": Cli,
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
    """
    Application contains an ui and a trader, ui and trader must inherit module class and implement a run method.

    1. Ui or trader fires an event via emit_event method
    2. Application receives the event, validates it, and places into apposite queue
    3. Trader or ui will retrieve a relative event.

    List of valid events is specified in events.py file.
    An event will have a name and some data.

    """

    def __init__(self, config_file: str) -> None:
        """ Initialize an ui and a trader based on given names """

        self.exit_event = ThreadEvent()
        signal(SIGINT, self.exit)
        signal(SIGTERM, self.exit)

        config = ConfigParser()
        config.read(config_file)
        self.ui_name = config["app"]["ui"]
        self.parser_name = config["app"]["parser"]
        self.trader_name = config["app"]["trader"]
        self.connector_name = config["app"]["connector"]

        self.ui_class: Type[Ui] = UIS[self.ui_name]
        self.parser_class: Type[Parser] = PARSERS[self.parser_name]
        self.trader_class: Type[Trader] = TRADERS[self.trader_name]
        self.connector_class: Type[Connector] = CONNECTORS[self.connector_name]

        self.ui_config: SectionProxy = config[self.ui_name]
        self.trader_config: SectionProxy = config[self.trader_name]

        self.ui_events: Queue = Queue()
        self.trader_events: Queue = Queue()

        self.parser: Parser = self.parser_class()
        self.ui: Ui = self.ui_class(self.ui_config, self.trader_events, self.exit_event, self.parser)
        self.connector: Connector = self.connector_class()
        self.trader: Trader = self.trader_class(self.trader_config, self.ui_events, self.exit_event, self.connector)

        self.ui.on_event(self.ui_event_handler)
        self.trader.on_event(self.trader_event_handler)

    def run(self):

        print("Starting Cihat-trader")

        self.ui.start()
        self.trader.start()

        self.ui.join()
        self.trader.join()

    def exit(self, signum, frame):

        print("Stopping Cihat-trader")

        self.exit_event.set()

    def ui_event_handler(self, ui_event: Event) -> None:
        if ui_event.name in UI_EVENTS:
            for data_entry in UI_EVENTS[ui_event.name]:
                if data_entry not in ui_event.data:
                    return
            self.ui_events.put(ui_event)

    def trader_event_handler(self, trader_event: Event):
        if trader_event.name in TRADER_EVENTS:
            for data_entry in TRADER_EVENTS[trader_event.name]:
                if data_entry not in trader_event.data:
                    return
            self.trader_events.put(trader_event)

