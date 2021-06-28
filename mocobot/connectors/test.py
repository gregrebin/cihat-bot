from mocobot.application.connector import Connector
from mocobot.application.connector import CandleEvent
from mocobot.application.order import Single
from mocobot.application.market import Interval, Candle
from asyncio import sleep
from typing import Tuple


class TestConnector(Connector):
    name = __name__

    async def on_run(self) -> None:
        self.log(f"""username {self.username}; password {self.password}""")
        while self.is_running:
            await sleep(3)
            self.emit(CandleEvent(name="Binance", symbol="BTCUSDT", interval=Interval(), candle=Candle()))

    def submit(self, execution_order: Single) -> Tuple[int, float]:
        pass

    def cancel(self, execution_order: Single) -> None:
        pass
