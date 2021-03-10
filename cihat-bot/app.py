from const import Constants
from ui import Ui
from trader import Trader
from events import Listener


class Application(Listener):

    def __init__(self, ui_name: str, trader_name: str) -> None:
        """ Initialize an ui and a trader based on given names """
        self.ui: Ui = Constants.UIS[ui_name](self)
        self.trader: Trader = Constants.TRADERS[trader_name](self)

    def event(self, event: str) -> None:
        """ Receives an event, call the appropriate function,
        operating on the trader in case of an ui event and on ui in case of the trader event """
        if event in Constants.UI_EVENTS:
            Constants.UI_EVENTS[event](self.trader)
        elif event in Constants.TRADER_EVENTS:
            Constants.TRADER_EVENTS[event](self.ui)

