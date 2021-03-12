from module import Module


class Trader(Module):

    def buy(self):
        self.emit_event("BOUGHT")

    def sell(self):
        self.emit_event("SOLD")
