from mocobot.application.order import Order
from mocobot.application.market import Market
from mocobot.application.ui import Ui, AddConnectorEvent
from asyncio import sleep


class TestUi(Ui):

    def pre_run(self) -> None:
        pass

    async def on_run(self) -> None:
        await sleep(10)
        self.emit(AddConnectorEvent(
            trader_name="test_trader", connector_name="test_connector",
            connector_username="test_username", connector_password="test_password")
        )

    def on_stop(self) -> None:
        pass

    def post_run(self) -> None:
        pass

    def update(self, order: Order, market: Market):
        pass

