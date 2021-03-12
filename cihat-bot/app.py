from const import *
from ui import Ui
from trader import Trader
from events import Listener, Emitter


class Application:

    def __init__(self, ui_name: str, trader_name: str) -> None:
        """ Initialize an ui and a trader based on given names """

        self.listener = Listener(self.event_handler)

        self.ui: Ui = UIS[ui_name]()
        self.ui.on_event(self.listener)

        self.trader: Trader = TRADERS[trader_name]()
        self.trader.on_event(self.listener)

    def event_handler(self, event: str) -> None:
        """ Receives an event, call the appropriate function,
        operating on the trader in case of an ui event and on th ui in case of a trader event """

        if event in UI_EVENTS:
            UI_EVENTS[event](self.trader)

        elif event in TRADER_EVENTS:
            TRADER_EVENTS[event](self.ui)

