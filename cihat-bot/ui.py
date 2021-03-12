from module import Module


class Ui(Module):

    def buy_cmd(self):
        self.emit_event("BUY")

    def sell_cmd(self):
        self.emit_event("SELL")

    def bought(self):
        pass

    def sold(self):
        pass
