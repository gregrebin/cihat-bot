from cihatbot.events import Event, NoEvent
from configparser import SectionProxy
from queue import Queue, Empty
from threading import Thread, Event as ThreadEvent
from typing import List, Callable


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

    def pre_run(self) -> None:
        pass

    def run(self) -> None:
        self.pre_run()
        while not self.exit_event.isSet():
            event = self.receive_event()
            self.loop(event)
        self.post_run()

    def loop(self, event: Event) -> None:
        pass

    def post_run(self):
        pass
