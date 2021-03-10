from ui import Ui
from trader import Trader
from typing import Dict, Type, Callable


class Constants:
    """ Concrete ui implementation classes """
    UIS: Dict[str, Type[Ui]] = {

    }
    """ Concrete trader implementation classes """
    TRADERS: Dict[str, Type[Trader]] = {

    }
    """ Events that can be emitted by ui, and the relative function on the trader """
    UI_EVENTS: Dict[str, Callable[[Trader], None]] = {

    }
    """ Events that can be emitted by trader, and the relative function on the ui """
    TRADER_EVENTS: Dict[str, Callable[[Ui], None]] = {

    }
