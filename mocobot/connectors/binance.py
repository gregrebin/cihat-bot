from mocobot.application.connector import Connector
from mocobot.application.order import Single, Command
from mocobot.application.market import Interval, TimeFrame
from binance import Client, ThreadedWebsocketManager
from binance.enums import *
from typing import Tuple, Type
from configparser import SectionProxy


class BinanceConnector(Connector):

    intervals = {
        Interval(1, TimeFrame.MINUTE): KLINE_INTERVAL_1MINUTE,
        Interval(3, TimeFrame.MINUTE): KLINE_INTERVAL_3MINUTE,
        Interval(5, TimeFrame.MINUTE): KLINE_INTERVAL_5MINUTE,
        Interval(15, TimeFrame.MINUTE): KLINE_INTERVAL_15MINUTE,
        Interval(30, TimeFrame.MINUTE): KLINE_INTERVAL_30MINUTE,
        Interval(1, TimeFrame.HOUR): KLINE_INTERVAL_1HOUR,
        Interval(2, TimeFrame.HOUR): KLINE_INTERVAL_2HOUR,
        Interval(4, TimeFrame.HOUR): KLINE_INTERVAL_4HOUR,
        Interval(6, TimeFrame.HOUR): KLINE_INTERVAL_6HOUR,
        Interval(8, TimeFrame.HOUR): KLINE_INTERVAL_8HOUR,
        Interval(12, TimeFrame.HOUR): KLINE_INTERVAL_12HOUR,
        Interval(1, TimeFrame.DAY): KLINE_INTERVAL_1DAY,
        Interval(3, TimeFrame.DAY): KLINE_INTERVAL_3DAY,
        Interval(1, TimeFrame.WEEK): KLINE_INTERVAL_1WEEK,
        Interval(1, TimeFrame.MONTH): KLINE_INTERVAL_1MONTH
    }

    def __init__(self, config: SectionProxy, category: Type, name: str, username: str, password: str):
        super().__init__(config, category, name, username, password)
        self.client: Client = Client(username, password)
        self.socket_manager: ThreadedWebsocketManager = ThreadedWebsocketManager(username, password)

    def pre_run(self) -> None:
        self.socket_manager.start()
        print("binance socket started")

    async def on_run(self) -> None:
        # self.start_trades("BTCBUSD")
        self.start_candles("BTCUSDT", Interval(1, TimeFrame.MINUTE))

    def on_stop(self) -> None:
        pass

    def post_run(self) -> None:
        self.socket_manager.stop()
        self.socket_manager.join()
        print("binance sockets stopped")

    def start_trades(self, symbol: str):
        self.socket_manager.start_aggtrade_socket(lambda msg: print(msg), symbol)

    def start_candles(self, symbol: str, interval: Interval):
        if interval in BinanceConnector.intervals:
            self.socket_manager.start_kline_socket(lambda msg: print(msg), symbol, BinanceConnector.intervals[interval])

    def submit(self, execution_order: Single) -> str:
        params = {"symbol": execution_order.symbol, "newClientOrderId": execution_order.uid,
                  "side": SIDE_BUY if execution_order.command is Command.BUY else SIDE_SELL}

        if execution_order.price > 0:
            params["type"] = ORDER_TYPE_LIMIT
            params["quantity"] = round(execution_order.quote, 6)
            params["price"] = execution_order.price
            params["timeInForce"] = TIME_IN_FORCE_GTC
        else:
            params["type"] = ORDER_TYPE_MARKET
            if execution_order.quote:
                params["quantity"] = execution_order.quote
            elif execution_order.base:
                params["quoteOrderQty"] = execution_order.base

        response = self.client.create_order(**params)
        return str(response["orderId"])

    def cancel(self, execution_order: Single) -> str:
        params = {"symbol": execution_order.symbol, "orderId": int(execution_order.eid), "origClientOrderId": execution_order.uid}
        response = self.client.cancel_order(**params)
        return response["clientOrderId"]
