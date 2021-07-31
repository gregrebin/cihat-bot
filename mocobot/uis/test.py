from mocobot.application.order import Order, Single, Mode
from mocobot.application.indicator import Indicator
from mocobot.application.market import Market
from mocobot.application.ui import Ui, AddConnectorEvent, AddOrderEvent
from asyncio import sleep


class TestUi(Ui):

    @property
    def static_site(self) -> str:
        return "http://help.websiteos.com/websiteos/example_of_a_simple_html_page.htm"

    def pre_run(self) -> None:
        pass

    async def on_run(self) -> None:
        pass

        # await sleep(10)
        # self.emit(AddConnectorEvent(
        #     connector_name="test_connector_no_args")
        # )

        # await sleep(2)
        # self.emit(AddConnectorEvent(connector_name="binance_connector"))

        # await sleep(2)
        # self.emit(AddOrderEvent(
        #     order=Single(exchange="binance", symbol="BTCBUSD", quote=10, price=20, indicators=(
        #         Indicator(name="price", min=10, max=10),
        #     )),
        #     mode=Mode.PARALLEL
        # ))

        # await sleep(2)
        # self.emit(AddConnectorEvent(connector_name="binance_connector"))

        # await sleep(2)
        # self.emit(AddConnectorEvent(connector_name="mxc_connector"))

        # await sleep(2)
        # self.emit(AddOrderEvent(
        #     order=Single(exchange="mxc", symbol="BTC_USDT", quote=10, price=20, indicators=(
        #         Indicator(name="price", min=10, max=10),
        #     )),
        #     mode=Mode.PARALLEL
        # ))

        # await sleep(2)
        # self.emit(AddConnectorEvent(connector_name="mxc_connector"))

        await sleep(2)
        self.emit(AddOrderEvent(
            order=Single(exchange="test", symbol="BTCUSDT", quote=10, price=20, time=1626990180),
            mode=Mode.PARALLEL
        ))

        await sleep(2)
        self.emit(AddOrderEvent(
            order=Single(exchange="test", symbol="BTCUSDT", quote=10, price=20, time=1626989820),
            mode=Mode.PARALLEL
        ))

    async def on_stop(self) -> None:
        pass

    def post_run(self) -> None:
        pass

    def update(self, order: Order, market: Market):
        pass

