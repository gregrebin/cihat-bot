from cihatbot.events import Listener, Emitter, Event


class Module:

    def __init__(self, config) -> None:
        self.emitter: Emitter = Emitter()
        self.config = config

    def on_event(self, listener: Listener):
        self.emitter.add_listener(listener)

    def emit_event(self, event: Event):
        self.emitter.emit(event)

    def run(self):
        pass
