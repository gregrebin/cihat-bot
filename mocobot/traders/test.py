from mocobot.application.order import Order
from mocobot.application.trader import Trader


class TestTrader(Trader):
    name = __name__

    def add_order(self, order: Order):
        pass

    def cancel_order(self, order: Order):
        pass

    def exchange_update(self):
        pass

    def ticker_update(self):
        pass
