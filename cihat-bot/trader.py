from events import Emitter, Listener


class Trader(Emitter):

    def __init__(self, event_listener: Listener):
        super().__init__(event_listener)

    def buy(self):
        pass

    def sell(self):
        pass
