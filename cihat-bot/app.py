from const import UIS, TRADERS, UI_EVENTS, TRADER_EVENTS
from ui import Ui
from trader import Trader
from events import Listener


class Application(Listener):

    def __init__(self, ui_name: str, trader_name: str) -> None:
        self.ui: Ui = UIS[ui_name](self)
        self.trader: Trader = TRADERS[trader_name](self)

    def event(self, event: str) -> None:
        if event in UI_EVENTS:
            UI_EVENTS[event](self.trader)
        elif event in TRADER_EVENTS:
            TRADER_EVENTS[event](self.ui)

