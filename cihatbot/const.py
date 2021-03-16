from cihatbot.module import Module
from cihatbot.traders.binance import Binance
from cihatbot.uis.cli import Cli
from typing import Dict, Type, Set


""" Concrete ui implementation classes """
UIS: Dict[str, Type[Module]] = {
    "cli": Cli
}

""" Concrete trader implementation classes """
TRADERS: Dict[str, Type[Module]] = {
    "binance": Binance
}

UI_EVENTS: Dict[str, Set[str]] = {
    "CONNECT": {"user", "password"},
    "EXECUTE": {"order"}
}

TRADER_EVENTS: Dict[str, Set[str]] = {
    "BOUGHT": set(),
    "SOLD": set()
}
