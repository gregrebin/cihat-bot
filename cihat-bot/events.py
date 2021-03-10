
class Listener:

    def event(self, event: str) -> None:
        pass


class Emitter:

    def __init__(self, listener: Listener) -> None:
        self.listener: Listener = listener

    def emit(self, event: str) -> None:
        self.listener.event(event)

