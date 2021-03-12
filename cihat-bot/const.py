from ui import Ui
from trader import Trader
from typing import Dict, Type, Callable


""" Concrete ui implementation classes """
UIS: Dict[str, Type[Ui]] = {
}

""" Concrete trader implementation classes """
TRADERS: Dict[str, Type[Trader]] = {
}

""" Events that can be emitted by ui, and the relative function on the trader """
UI_EVENTS: Dict[str, Callable[[Trader], None]] = {
    "BUY": lambda trader: trader.buy(),
    "SELL": lambda trader: trader.sell()
}

""" Events that can be emitted by trader, and the relative function on the ui """
TRADER_EVENTS: Dict[str, Callable[[Ui], None]] = {
    "BOUGHT": lambda ui: ui.bought(),
    "SOLD": lambda ui: ui.sold()
}
