from mocobot.application.connector import Connector
from mocobot.application.connector import CandleEvent
from mocobot.application.order import Single
from mocobot.application.market import Interval, Candle
from asyncio import sleep
from typing import Tuple


class TestConnector(Connector):

    @property
    def exchange(self) -> str:
        return "test"

    def pre_run(self) -> None:
        pass

    async def on_run(self) -> None:
        self.log(f"Running with user {self.username} and password {self.password}")
        # while self.is_running:
        #     await sleep(3)
        #     self.emit(CandleEvent(name="test", symbol="BTCUSDT", interval=Interval(3), candle=Candle()))

    def on_stop(self) -> None:
        pass

    def post_run(self) -> None:
        pass

    def start_candles(self, symbol: str, interval: Interval) -> None:
        self.log(f"Start candles for {symbol} {interval}")

    def submit(self, execution_order: Single) -> str:
        pass

    def cancel(self, execution_order: Single) -> str:
        pass
