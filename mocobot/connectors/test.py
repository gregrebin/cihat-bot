from mocobot.application.connector import Connector
from mocobot.application.connector import CandleEvent
from mocobot.application.order import Single
from mocobot.application.market import Interval, Candle
from asyncio import sleep
from typing import Tuple


class TestConnector(Connector):

    def pre_run(self) -> None:
        pass

    async def on_run(self) -> None:
        while self.is_running:
            await sleep(3)
            self.emit(CandleEvent(name="Binance", symbol="BTCUSDT", interval=Interval(), candle=Candle()))

    def on_stop(self) -> None:
        pass

    def post_run(self) -> None:
        pass

    def submit(self, execution_order: Single) -> Tuple[int, float]:
        pass

    def cancel(self, execution_order: Single) -> None:
        pass
