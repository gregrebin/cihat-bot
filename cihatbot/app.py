from cihatbot.const import *
from cihatbot.events import Listener, Event
from configparser import ConfigParser
from queue import Queue


class Application:
    """
    Application contains an ui and a trader, ui and trader must inherit module class and implement a run method.

    1. Ui or trader fires an event via emit_event method
    2. Application receives the event, validates it, and places into apposite queue
    3. Trader or ui will retrieve a relative event.

    List of valid events is specified in const.py file.
    An event will have a name and some data.

    """

    def __init__(self, ui_name: str, trader_name: str, config_file: str) -> None:
        """ Initialize an ui and a trader based on given names """

        config = ConfigParser()
        config.read(config_file)

        self.ui_events = Queue()
        self.trader_events = Queue()

        self.ui_listener = Listener(self.ui_event_handler)
        self.trader_listener = Listener(self.trader_event_handler)

        self.ui_class = UIS[ui_name]
        self.trader_class = TRADERS[trader_name]

        self.ui_config = config[ui_name]
        self.trader_config = config[trader_name]

        self.ui: Module = self.ui_class(self.ui_config, self.trader_events)
        self.trader: Module = self.trader_class(self.trader_config, self.ui_events)

        self.ui.on_event(self.ui_listener)
        self.trader.on_event(self.trader_listener)

    def run(self):

        self.ui.start()
        self.trader.start()

        self.ui.join()
        self.trader.join()

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

