from cihatbot.application.order import Order
from cihatbot.application.ui import Ui, AddModuleEvent
from asyncio import sleep


class TestUi(Ui):
    log_name = __name__

    async def on_run(self) -> None:
        await super().on_run()
        await sleep(10)
        self.emit(AddModuleEvent(connector_name="binance_connector", connector_username="test_username", connector_password="test_password"))

    def trades_update(self, order: Order):
        pass