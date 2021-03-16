from cihatbot.events import Event, NoEvent
from threading import Thread
from queue import Queue, Empty
from typing import List, Callable
from configparser import SectionProxy
from threading import Event as ThreadEvent


class Module(Thread):

    def __init__(self, config: SectionProxy, queue: Queue, exit_event: ThreadEvent) -> None:
        super().__init__()
        self.config: SectionProxy = config
        self.queue: Queue = queue
        self.exit_event: ThreadEvent = exit_event
        self.listeners: List[Callable[[Event], None]] = []

    def on_event(self, listener: Callable[[Event], None]) -> None:
        self.listeners.append(listener)

    def emit_event(self, event: Event) -> None:
        for listener in self.listeners:
            listener(event)

    def receive_event(self) -> Event:
        try:
            event = self.queue.get(block=False)
        except Empty:
            event = NoEvent()
        return event

    def run(self) -> None:
        while not self.exit_event.isSet():
            event = self.receive_event()
            self.loop(event)

    def loop(self, event: Event) -> None:
        pass
