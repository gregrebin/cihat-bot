from cihatbot.events import Listener, Emitter, Event
from cihatbot.utils.execution_order import Parser, ExecutionOrder
from threading import Thread
from queue import Queue, Empty


class Module(Thread):

    def __init__(self, config, queue) -> None:
        super().__init__()
        self.emitter: Emitter = Emitter()
        self.config = config
        self.queue: Queue = queue

    def on_event(self, listener: Listener) -> None:
        self.emitter.add_listener(listener)

    def emit_event(self, event: Event) -> None:
        self.emitter.emit(event)

    def run(self) -> None:
        while True:
            try:
                event = self.queue.get(block=False)
            except Empty:
                event = None
            self.loop(event)

    def loop(self, event: Event) -> None:
        pass
