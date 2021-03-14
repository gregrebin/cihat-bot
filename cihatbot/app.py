from cihatbot.const import *
from cihatbot.ui import Ui
from cihatbot.trader import Trader
from cihatbot.events import Listener, Event
from configparser import ConfigParser


class Application:
    """
    Application contains an ui and a trader,
    ui and trader must inherit module class.

    1. Ui or trader fires an event via emit_event method
    2. Application receives the event and validates it
    3. Application call the apposite method on trader or ui

    List of events and relative method are contained in const.py file.
    An event will have a name and some data:
    The name defines the event and the data will be passed to the relative method.

    """

    def __init__(self, ui_name: str, trader_name: str, config_file: str) -> None:
        """ Initialize an ui and a trader based on given names """

        config = ConfigParser()
        config.read(config_file)

        self.ui: Ui = UIS[ui_name](config[ui_name])
        self.ui.on_event(Listener(self.ui_event_handler))

        self.trader: Trader = TRADERS[trader_name](config[trader_name])
        self.trader.on_event(Listener(self.trader_event_handler))

    def run(self):
        self.ui.run()
        self.trader.run()

    def ui_event_handler(self, ui_event: Event) -> None:
        if ui_event.name in UI_EVENTS:
            UI_EVENTS[ui_event.name](self.trader, ui_event)

    def trader_event_handler(self, trader_event: Event):
        if trader_event.name in TRADER_EVENTS:
            TRADER_EVENTS[trader_event.name](self.ui, trader_event)

