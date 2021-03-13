from cihatbot.const import *
from cihatbot.ui import Ui
from cihatbot.trader import Trader
from cihatbot.events import Listener, Emitter
from configparser import ConfigParser
import asyncio


class Application:

    def __init__(self, ui_name: str, trader_name: str, config_file: str) -> None:
        """ Initialize an ui and a trader based on given names """

        config = ConfigParser()
        config.read(config_file)

        self.ui: Ui = UIS[ui_name](config[ui_name])
        self.ui.on_event(Listener(self.ui_event_handler))

        self.trader: Trader = TRADERS[trader_name](config[trader_name])
        self.trader.on_event(Listener(self.trader_event_handler))

    def run(self):
        self.trader.run()
        self.ui.run()

    def ui_event_handler(self, event: str) -> None:
        if event in UI_EVENTS:
            UI_EVENTS[event](self.trader)

    def trader_event_handler(self, event: str):
        if event in TRADER_EVENTS:
            TRADER_EVENTS[event](self.ui)

