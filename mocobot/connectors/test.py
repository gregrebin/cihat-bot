from mocobot.application.connector import Connector, CandleEvent, Recipe, Status
from mocobot.application.order import Single
from mocobot.application.market import Interval, Candle
from asyncio import sleep
from time import time
from typing import Tuple


class TestConnector(Connector):

    @property
    def exchange(self) -> str:
        return "test"

    def pre_run(self) -> None:
        pass

    async def on_run(self) -> None:
        self.log(f"Running with user {self.username} and password {self.password}")
        price = 0
        while self.is_running:
            await sleep(2)
            self.emit(CandleEvent(exchange="test", symbol="BTCUSDT", interval=Interval(), candle=Candle(time=int(time()), close=price)))
            price += 1

    def on_stop(self) -> None:
        pass

    def post_run(self) -> None:
        pass

    def start_candles(self, symbol: str, interval: Interval) -> None:
        self.log(f"Start candles for {symbol} {interval}")

    def submit(self, order: Single) -> Recipe:
        self.log(f"Submit {order}")
        return Recipe(eid="007", status=Status.SUBMITTED)

    def cancel(self, order: Single) -> Recipe:
        return Recipe(eid=order.eid, status=Status.CANCELLED)
