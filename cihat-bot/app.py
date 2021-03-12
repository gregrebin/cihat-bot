from const import *
from ui import Ui
from trader import Trader
from events import Listener, Emitter


class Application:

    def __init__(self, ui_name: str, trader_name: str) -> None:
        """ Initialize an ui and a trader based on given names """

        self.ui: Ui = UIS[ui_name]()
        self.ui.on_event(Listener(self.ui_event_handler))

        self.trader: Trader = TRADERS[trader_name]()
        self.trader.on_event(Listener(self.trader_event_handler))

    def ui_event_handler(self, event: str) -> None:
        if event in UI_EVENTS:
            UI_EVENTS[event](self.trader)

    def trader_event_handler(self, event: str):
        if event in TRADER_EVENTS:
            TRADER_EVENTS[event](self.ui)

