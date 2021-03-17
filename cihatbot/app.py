from cihatbot.module import Module
from cihatbot.events import Event, UI_EVENTS, TRADER_EVENTS
from cihatbot.uis.cli import Cli
from cihatbot.uis.telegram import Telegram
from cihatbot.traders.binance import Binance
from configparser import ConfigParser, SectionProxy
from queue import Queue
from typing import Type, Dict
from threading import Event as ThreadEvent
from signal import signal, SIGINT, SIGTERM


""" Concrete ui implementation classes """
UIS: Dict[str, Type[Module]] = {
    "cli": Cli,
    "telegram": Telegram
}

""" Concrete trader implementation classes """
TRADERS: Dict[str, Type[Module]] = {
    "binance": Binance
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

    def __init__(self, ui_name: str, trader_name: str, config_file: str) -> None:
        """ Initialize an ui and a trader based on given names """

        config = ConfigParser()
        config.read(config_file)

        self.exit_event = ThreadEvent()
        signal(SIGINT, self.exit)
        signal(SIGTERM, self.exit)

        self.ui_events: Queue = Queue()
        self.trader_events: Queue = Queue()

        self.ui_class: Type[Module] = UIS[ui_name]
        self.trader_class: Type[Module] = TRADERS[trader_name]

        self.ui_config: SectionProxy = config[ui_name]
        self.trader_config: SectionProxy = config[trader_name]

        self.ui: Module = self.ui_class(self.ui_config, self.trader_events, self.exit_event)
        self.trader: Module = self.trader_class(self.trader_config, self.ui_events, self.exit_event)

        self.ui.on_event(self.ui_event_handler)
        self.trader.on_event(self.trader_event_handler)

    def run(self):

        self.ui.start()
        self.trader.start()

        self.ui.join()
        self.trader.join()

    def exit(self, signum, frame):
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

