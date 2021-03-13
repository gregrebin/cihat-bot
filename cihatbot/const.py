from cihatbot.ui import Ui
from cihatbot.trader import Trader
from cihatbot.traders.binance import Binance
from cihatbot.uis.cli import Cli
from typing import Dict, Type, Callable


""" Concrete ui implementation classes """
UIS: Dict[str, Type[Ui]] = {
    "cli": Cli
}

""" Concrete trader implementation classes """
TRADERS: Dict[str, Type[Trader]] = {
    "binance": Binance
}

""" Events that can be emitted by ui, and the relative function on the trader """
UI_EVENTS: Dict[str, Callable[[Trader, Dict[str, str]], None]] = {
    "BUY": lambda trader, data: trader.buy(data),
    "SELL": lambda trader, data: trader.sell(data)
}

""" Events that can be emitted by trader, and the relative function on the ui """
TRADER_EVENTS: Dict[str, Callable[[Ui, Dict[str, str]], None]] = {
    "BOUGHT": lambda ui, data: ui.bought(data),
    "SOLD": lambda ui, data: ui.sold(data)
}
