from const import *
from ui import Ui
from trader import Trader
from events import Listener


class Application(Listener):

    def __init__(self, ui_name: str, trader_name: str) -> None:
        """ Initialize an ui and a trader based on given names """
        self.ui: Ui = UIS[ui_name](self)
        self.trader: Trader = TRADERS[trader_name](self)

    def event(self, event: str) -> None:
        """ Receives an event, call the appropriate function,
        operating on the trader in case of an ui event and on th ui in case of a trader event """
        if event in UI_EVENTS:
            UI_EVENTS[event](self.trader)
        elif event in TRADER_EVENTS:
            TRADER_EVENTS[event](self.ui)

