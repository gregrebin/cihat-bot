from __future__ import annotations
from cihatbot.logger import Logger
from cihatbot.events import UserEvent, TickerEvent
from cihatbot.connector.connector import Connector, ConnectorException, FailedException
from cihatbot.execution_order.execution_order import SingleExecutionOrder, ExecutionConditions, ExecutionParams
from binance.client import Client
from binance.exceptions import BinanceOrderException, BinanceRequestException, BinanceAPIException
from binance.websockets import BinanceSocketManager
from functools import reduce
from queue import Queue
from typing import Callable, Dict, List, Tuple
import logging


class BinanceConnector(Connector):

    BINANCE_ORDER_STATUS_NEW = "NEW"
    BINANCE_ORDER_STATUS_P_FILLED = "PARTIALLY_FILLED"
    BINANCE_ORDER_STATUS_FILLED = "FILLED"
    BINANCE_ORDER_STATUS_CANCELED = "CANCELED"
    BINANCE_ORDER_STATUS_GOOD = (BINANCE_ORDER_STATUS_NEW, BINANCE_ORDER_STATUS_P_FILLED, BINANCE_ORDER_STATUS_FILLED)

    def __init__(self):

        super().__init__()
        self.logger: Logger = Logger(__name__, logging.INFO)
        self.client: Client = Client("", "")
        self.socket = BinanceSocketManager(self.client)
        self.connected: bool = False

    def connect(self, key: str, secret: str) -> None:

        self.client = Client(api_key=key, api_secret=secret)
        self.socket = BinanceSocketManager(self.client)
        self.connected = True

    def start_listen(self):

        if not self.connected:
            return

        self.socket.start_user_socket(self.user_handler)
        self.socket.start_miniticker_socket(self.ticker_handler)
        self.socket.daemon = True
        self.socket.start()

    def user_handler(self, message: Dict):

        message_type = message["e"]
        if not message_type == "executionReport":
            return

        order_id = message["i"]
        binance_order_status = message["X"]

        if binance_order_status == BinanceConnector.BINANCE_ORDER_STATUS_FILLED:
            self.emit(UserEvent({"external_id": order_id, "status": BinanceConnector.ORDER_STATUS_FILLED}))
        elif binance_order_status == BinanceConnector.BINANCE_ORDER_STATUS_CANCELED:
            self.emit(UserEvent({"external_id": order_id, "status": BinanceConnector.ORDER_STATUS_CANCELED}))

    def ticker_handler(self, message: List[Dict]):

        for ticker in message:

            message_type = ticker["e"]
            if not message_type == "24hrMiniTicker":
                continue

        self.emit(TickerEvent({}))

    def stop_listen(self):

        self.socket.close()

    def satisfied(self, execution_order: SingleExecutionOrder) -> bool:

        execution_conditions = execution_order.conditions
        return True

    def submit(self, execution_order: SingleExecutionOrder) -> int:

        execution_params = execution_order.params
        is_market = execution_params.price == 0
        is_all_in = execution_params.quantity == 0

        side = self.client.SIDE_BUY
        if execution_params.command == ExecutionParams.CMD_SELL:
            side = self.client.SIDE_SELL

        params = {
            "newClientOrderId": execution_order.order_id,
            "symbol": execution_params.symbol,
            "side": side,
        }

        if is_all_in:
            params["quantity"] = self._order_book_depth(execution_params.command, execution_params.symbol)
        else:
            params["quantity"] = execution_params.quantity

        if is_market:
            params["type"] = self.client.ORDER_TYPE_MARKET
        else:
            params["type"] = self.client.ORDER_TYPE_LIMIT
            params["price"] = execution_params.price
            params["timeInForce"] = self.client.TIME_IN_FORCE_GTC

        try:
            binance_order = self.client.create_order(**params)
            if binance_order["status"] not in BinanceConnector.BINANCE_ORDER_STATUS_GOOD:
                raise FailedException(f"""Order {binance_order["status"]}""", execution_order)

        except (BinanceRequestException, BinanceOrderException, BinanceAPIException) as exception:
            raise ConnectorException(exception.message, execution_order)

        self.logger.log(logging.INFO, f"""Submitted order: {execution_order}; status: {binance_order["status"]}""")
        return binance_order["orderId"]

    def _order_book_depth(self, command: str, symbol: str) -> float:

        depth = 0.0
        order_book = self.client.get_order_book(symbol=symbol, limit=5000)

        if command == ExecutionParams.CMD_SELL:
            book = order_book["bids"]
        else:
            book = order_book["asks"]

        for order in book:
            quantity = float(order[1])
            depth += quantity

        return depth

    def is_filled(self, execution_order: SingleExecutionOrder) -> bool:

        try:
            binance_order = self.client.get_order(
                symbol=execution_order.params.symbol,
                orderId=execution_order.external_id
            )
        except (BinanceRequestException, BinanceAPIException) as exception:
            raise ConnectorException(exception.message, execution_order)

        return binance_order["status"] == self.client.ORDER_STATUS_FILLED

    def cancel(self, execution_order: SingleExecutionOrder) -> None:

        try:
            self.client.cancel_order(
                symbol=execution_order.params.symbol,
                orderId=execution_order.external_id
            )
        except (BinanceRequestException, BinanceAPIException) as exception:
            raise ConnectorException(exception.message, execution_order)
