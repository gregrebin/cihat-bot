from events import Emitter, Listener


class Ui(Emitter):

    def __init__(self, event_listener: Listener):
        super().__init__(event_listener)

    def bought(self):
        pass

    def sold(self):
        pass
