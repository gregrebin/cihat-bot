from events import Listener, Emitter


class Module:

    def __init__(self) -> None:
        self.emitter: Emitter = Emitter()

    def on_event(self, listener: Listener):
        self.emitter.add_listener(listener)

    def emit_event(self, event: str):
        self.emitter.emit(event)
