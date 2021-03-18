from typing import Dict, Any, Set


UI_EVENTS: Dict[str, Set[str]] = {
    "CONNECT": {"user", "password"},
    "EXECUTE": {"order"}
}

TRADER_EVENTS: Dict[str, Set[str]] = {
    "FILLED": {"single_order"},
}


class Event:

    def __init__(self, name: str, data: Dict[str, Any]):
        self.name: str = name
        self.data: Dict[str, Any] = data


class NoEvent(Event):

    def __init__(self):
        super().__init__("NONE", {})
