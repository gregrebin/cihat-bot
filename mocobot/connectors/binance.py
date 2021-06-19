from mocobot.application.connector import Connector
from mocobot.application.connector import TickerEvent
from mocobot.application.order import Single
from asyncio import sleep
from typing import Tuple


class BinanceConnector(Connector):
    name = __name__

    async def on_run(self) -> None:
        self.log(f"""username {self.username}; password {self.password}""")
        while self.is_running:
            await sleep(5)
            self.emit(TickerEvent())

    def submit(self, execution_order: Single) -> Tuple[int, float]:
        pass

    def cancel(self, execution_order: Single) -> None:
        pass
