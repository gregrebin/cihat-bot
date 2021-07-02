from mocobot.application.connector import Connector
from mocobot.application.connector import CandleEvent
from mocobot.application.order import Single, Command
from binance import Client
from binance.enums import SIDE_BUY, SIDE_SELL, ORDER_TYPE_LIMIT, ORDER_TYPE_MARKET, TIME_IN_FORCE_GTC
from asyncio import sleep
from typing import Tuple, Type
from configparser import SectionProxy


class BinanceConnector(Connector):

    def __init__(self, config: SectionProxy, category: Type, name: str, username: str, password: str):
        super().__init__(config, category, name, username, password)
        self.client: Client = Client(username, password)

    def pre_run(self) -> None:
        pass

    async def on_run(self) -> None:
        pass

    def on_stop(self) -> None:
        pass

    def post_run(self) -> None:
        pass

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
