from typing import Generator

from mocobot.application.order import Order
from mocobot.application.trader import Trader, Submit
from mocobot.application.market import Market


class TestTrader(Trader):

    def pre_run(self) -> None:
        pass

    async def on_run(self) -> None:
        pass

    def on_stop(self) -> None:
        pass

    def post_run(self) -> None:
        pass

    def update(self, order: Order, market: Market) -> Generator[Submit, None, None]:
        return
        yield

