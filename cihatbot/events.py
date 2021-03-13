from typing import Callable, List


class Listener:

    def __init__(self, handler: Callable[[str], None]):
        self.handler = handler

    def event(self, event: str) -> None:
        self.handler(event)


class Emitter:

    def __init__(self) -> None:
        self.listeners: List[Listener] = []

    def add_listener(self, listener: Listener):
        self.listeners.append(listener)

    def remove_listener(self, listener: Listener):
        self.listeners.remove(listener)

    def emit(self, event: str) -> None:
        for listener in self.listeners:
            listener.event(event)

