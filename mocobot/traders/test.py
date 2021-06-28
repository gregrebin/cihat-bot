from mocobot.application.order import Order
from mocobot.application.trader import Trader
from mocobot.application.market import Market


class TestTrader(Trader):
    name = __name__

    def add_order(self, order: Order, market: Market) -> None:
        pass

    def cancel_order(self, order: Order, market: Market) -> None:
        pass

    def new_trade(self, order: Order, market: Market) -> None:
        pass

    def new_candle(self, order: Order, market: Market) -> None:
        pass
