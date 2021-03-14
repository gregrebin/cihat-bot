from cihatbot.events import Listener, Emitter, Event
from cihatbot.modules.execution_order import Parser, ExecutionOrder


class Module:

    def __init__(self, config) -> None:
        self.emitter: Emitter = Emitter()
        self.parser = Parser()
        self.config = config

    def parse(self, order_description: str) -> ExecutionOrder:
        return self.parser.parse(order_description)

    def on_event(self, listener: Listener) -> None:
        self.emitter.add_listener(listener)

    def emit_event(self, event: Event) -> None:
        self.emitter.emit(event)

    def run(self) -> None:
        pass
