from cihatbot.events import Event, NoEvent, EventEmitter, EventListener
from queue import Queue, Empty
from threading import Thread, Event as ThreadEvent
from typing import List, Callable, Dict


class Module(Thread):

    def __init__(self, config: Dict) -> None:
        super().__init__()
        self.config: Dict = config
        self.emitter: EventEmitter = EventEmitter()
        self.listener: EventListener = EventListener()

    def emit_event(self, event: Event) -> None:
        self.emitter.emit(event)

    def add_listener(self, listener: EventListener):
        self.emitter.add_listener(listener)

    def pre_run(self) -> None:
        pass

    def run(self) -> None:
        self.pre_run()
        self.listener.listen(self.on_event)
        self.post_run()

    def on_event(self, event: Event):
        pass

    def loop(self, event: Event) -> None:
        pass

    def post_run(self):
        pass

    def stop(self):
        self.listener.stop()
