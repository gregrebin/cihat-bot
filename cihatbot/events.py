from queue import Queue
from typing import Dict, Any, Set, List, Callable


UI_EVENTS: Dict[str, Set[str]] = {
    "CONNECT": {"user", "password"},
    "ADD": {"order", "mode"},
    "DELETE": {"order_id"}
}

TRADER_EVENTS: Dict[str, Set[str]] = {
    "CONNECTED": {"user"},
    "ADDED": {"all", "single"},
    "DELETED": {"all", "order_id"},
    "SUBMITTED": {"all", "single"},
    "FILLED": {"all", "single"},
    "ERROR": {"order", "message"}
}

USER_EVENTS: Dict[str, Set[str]] = {
    "ADD_TRADER": {"trader_name", "connector_name", "config"},
    "ADD_UI": {"ui_name", "parser_name", "config"}
}

APP_EVENTS: Dict[str, Set[str]] = {
    "NEW_USER": {"ui", "parser", "trader", "connector"}
}


class Event:

    def __init__(self, name: str, data: Dict[str, Any]):
        self.name: str = name
        self.data: Dict[str, Any] = data

    def __str__(self):
        return f"""{self.name} - {self.data}"""


class StopEvent(Event):

    NAME = "STOP"

    def __init__(self):
        super().__init__(StopEvent.NAME, {})


class EventListener:

    def __init__(self):
        self.queue: Queue = Queue()

    def listen(self, on_event: Callable[[Event], None]):
        stop = False
        while not stop:
            event = self.queue.get()
            on_event(event)
            stop = event.name == StopEvent.NAME

    def stop(self):
        self.queue.put(StopEvent())


class EventEmitter:

    def __init__(self):
        self.listeners: List[Queue] = []

    def add_listener(self, listener: EventListener):
        self.listeners.append(listener.queue)

    def emit(self, event: Event):
        for listener in self.listeners:
            listener.put(event)
