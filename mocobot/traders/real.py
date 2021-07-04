from mocobot.application.market import Market
from mocobot.application.order import Order
from mocobot.application.trader import Trader, Submit
from mocobot.application.connector import Connector
from typing import Generator


class RealTrader(Trader):

    def pre_run(self) -> None:
        pass

    async def on_run(self) -> None:
        pass

    def on_stop(self) -> None:
        pass

    def post_run(self) -> None:
        pass

    def update(self, order: Order, market: Market) -> Generator[Submit, None, None]:
        for order in order.get():
            # TODO: check conditions
            for connector in self.get_submodule(Connector, exchange=order.exchange):
                eid = connector.submit(order)
                yield Submit(uid=order.uid, eid=eid)
