from typing import Tuple

from mocobot.application.market import Market
from mocobot.application.order import Order
from mocobot.application.trader import Trader, Submit


class RealTrader(Trader):

    def pre_run(self) -> None:
        pass

    async def on_run(self) -> None:
        pass

    def on_stop(self) -> None:
        pass

    def post_run(self) -> None:
        pass

    def update(self, order: Order, market: Market) -> Tuple[Submit, ...]:
        pass
