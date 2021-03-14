from typing import Callable, List, Dict, Any


class Event:

    def __init__(self, name: str, data: Dict[str, Any]):
        self.name: str = name
        self.data: Dict[str, Any] = data


class Listener:

    def __init__(self, handler: Callable[[Event], None]):
        self.handler: Callable[[Event], None] = handler

    def event(self, event: Event) -> None:
        self.handler(event)


class Emitter:

    def __init__(self) -> None:
        self.listeners: List[Listener] = []

    def add_listener(self, listener: Listener):
        self.listeners.append(listener)

    def remove_listener(self, listener: Listener):
        self.listeners.remove(listener)

    def emit(self, event: Event) -> None:
        for listener in self.listeners:
            listener.event(event)

