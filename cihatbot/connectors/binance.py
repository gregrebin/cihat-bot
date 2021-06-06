from cihatbot.application.connector import Connector
from cihatbot.application.connector import TickerEvent
from cihatbot.application.order import SingleExecutionOrder
from asyncio import sleep
from typing import Tuple


class BinanceConnector(Connector):
    log_name = __name__

    async def on_run(self) -> None:
        self.log(f"""username {self.username}; password {self.password}""")
        while self.is_running:
            await sleep(5)
            self.emit(TickerEvent())

    def submit(self, execution_order: SingleExecutionOrder) -> Tuple[int, float]:
        pass

    def cancel(self, execution_order: SingleExecutionOrder) -> None:
        pass
