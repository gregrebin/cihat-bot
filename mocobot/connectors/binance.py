from mocobot.application.connector import Connector
from mocobot.application.connector import CandleEvent
from mocobot.application.order import Single
from asyncio import sleep
from typing import Tuple


class BinanceConnector(Connector):

    def pre_run(self) -> None:
        pass

    async def on_run(self) -> None:
        pass

    def on_stop(self) -> None:
        pass

    def post_run(self) -> None:
        pass

    def submit(self, execution_order: Single) -> Tuple[int, float]:
        pass

    def cancel(self, execution_order: Single) -> None:
        pass
