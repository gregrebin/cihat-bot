from cihatbot.events import Event
from cihatbot.modules.ui import Ui
from cihatbot.modules.trader import Trader
from cihatbot.traders.binance import Binance
from cihatbot.uis.cli import Cli
from typing import Dict, Type, Callable, Set


""" Concrete ui implementation classes """
UIS: Dict[str, Type[Ui]] = {
    "cli": Cli
}

""" Concrete trader implementation classes """
TRADERS: Dict[str, Type[Trader]] = {
    "binance": Binance
}

""" Events that can be emitted by ui, and the relative function on the trader """
UI_EVENTS: Dict[str, Callable[[Trader, Event], None]] = {
    "CONNECT": lambda trader, event: trader.connect(event),
    "EXECUTE": lambda trader, event: trader.execute(event)
}

UI_EVENTS_DATA: Dict[str, Set[str]] = {
    "CONNECT": {"user", "password"},
    "EXECUTE": {"order"}
}

""" Events that can be emitted by trader, and the relative function on the ui """
TRADER_EVENTS: Dict[str, Callable[[Ui, Event], None]] = {
    "BOUGHT": lambda ui, event: ui.bought(event),
    "SOLD": lambda ui, event: ui.sold(event)
}

TRADER_EVENTS_DATA: Dict[str, Set[str]] = {
    "BOUGHT": set(),
    "SOLD": set()
}
