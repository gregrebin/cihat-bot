from mocobot.application.market import Market
from mocobot.application.order import Order
from mocobot.application.trader import Trader


class RealTrader(Trader):

    def add_order(self, order: Order, market: Market) -> None:
        pass

    def cancel_order(self, order: Order, market: Market) -> None:
        pass

    def new_trade(self, order: Order, market: Market) -> None:
        pass

    def new_candle(self, order: Order, market: Market) -> None:
        pass

    def pre_run(self) -> None:
        pass

    async def on_run(self) -> None:
        pass

    def on_stop(self) -> None:
        pass

    def post_run(self) -> None:
        pass
