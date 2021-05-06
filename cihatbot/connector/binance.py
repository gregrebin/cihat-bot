from __future__ import annotations
from cihatbot.application.events import UserEvent, TickerEvent
from cihatbot.connector.connector import Connector, ConnectorException, FailedException
from cihatbot.execution_order.execution_order import SingleExecutionOrder, ExecutionConditions, ExecutionParams
from binance.client import Client
from binance.exceptions import BinanceOrderException, BinanceRequestException, BinanceAPIException
from binance.websockets import BinanceSocketManager
from functools import reduce
from queue import Queue
from typing import Dict, List, Tuple, Any
import logging


class BinanceConnector(Connector):

    log_name = __name__

    BINANCE_ORDER_STATUS_NEW = "NEW"
    BINANCE_ORDER_STATUS_P_FILLED = "PARTIALLY_FILLED"
    BINANCE_ORDER_STATUS_FILLED = "FILLED"
    BINANCE_ORDER_STATUS_CANCELED = "CANCELED"
    BINANCE_ORDER_STATUS_GOOD = (BINANCE_ORDER_STATUS_NEW, BINANCE_ORDER_STATUS_P_FILLED, BINANCE_ORDER_STATUS_FILLED)

    def __init__(self):

        super().__init__()
        self.client: Client = Client("", "")
        self.socket = BinanceSocketManager(self.client)
        self.connected: bool = False

    def connect(self, key: str, secret: str) -> None:

        self.client = Client(api_key=key, api_secret=secret)
        self.socket = BinanceSocketManager(self.client)
        self.socket.start_user_socket(self.user_handler)
        self.socket.start_miniticker_socket(self.ticker_handler)
        self.socket.daemon = True
        self.socket.start()
        self.connected = True

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

    def post_run(self) -> None:

        super().post_run()
        if self.connected:
            self.socket.close()

    def satisfied(self, execution_order: SingleExecutionOrder) -> bool:

        execution_conditions = execution_order.conditions
        return True

    def submit(self, execution_order: SingleExecutionOrder) -> int:

        execution_params = execution_order.params
        is_market_fast = execution_params.price == 0.0
        is_market_wait = execution_params.price == -1.0
        is_market = execution_params.price == -2.0

        side = self.client.SIDE_BUY
        if execution_params.command == ExecutionParams.CMD_SELL:
            side = self.client.SIDE_SELL

        params = {
            "newClientOrderId": execution_order.order_id,
            "symbol": execution_params.symbol,
            "side": side,
            "quantity": execution_params.quantity
        }

        if is_market or is_market_fast or is_market_wait:
            params["type"] = self.client.ORDER_TYPE_MARKET
        else:
            params["type"] = self.client.ORDER_TYPE_LIMIT
            params["price"] = execution_params.price
            params["timeInForce"] = self.client.TIME_IN_FORCE_GTC

        binance_order, failed = self._submit(execution_order, params)

        if failed and is_market_fast:
            self.log(f"""Failed order: {execution_order}; status: {binance_order["status"]}""")
            params["quantity"] = self._order_book_depth(execution_params.command, execution_params.symbol)
            self.log(f"""Trying with quantity: {params["quantity"]}""")
            binance_order, failed = self._submit(execution_order, params)

        elif failed and is_market_wait:
            self.log(f"""Failed order: {execution_order}; status: {binance_order["status"]}""")
            self._wait_order_book(execution_params.quantity, execution_params.command, execution_params.symbol)
            self.log(f"""Trying again""")
            binance_order, failed = self._submit(execution_order, params)

        if failed:
            self.log(f"""Failed order: {execution_order}; status: {binance_order["status"]}""")
            self.log(f"""Raising failed exception""")
            raise FailedException(f"""Order {binance_order["status"]}""", execution_order)

        self.log(f"""Submitted order: {execution_order}; status: {binance_order["status"]}""")
        return binance_order["orderId"]

    def _submit(self, execution_order: SingleExecutionOrder, params: Dict[str, Any]) -> Tuple[dict, bool]:

        try:
            binance_order = self.client.create_order(**params)

        except (BinanceRequestException, BinanceOrderException, BinanceAPIException) as exception:
            self.log(f"""Binance exception: {exception.message}""")
            raise ConnectorException(exception.message, execution_order)

        return binance_order, binance_order["status"] not in BinanceConnector.BINANCE_ORDER_STATUS_GOOD

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

        print(f"""Order book depth: {depth}""")
        return depth

    def _wait_order_book(self, quantity: float, command: str, symbol: str):

        messages = Queue()
        socket_number = self.socket.start_depth_socket(symbol, lambda msg: messages.put(msg))

        book, last_update_id = self._book_snapshot(command, symbol)

        while reduce(lambda q1, q2: q1 + q2, book.values()) < quantity:
            print(f"""Wait order book (looking for {quantity}): {reduce(lambda q1, q2: q1 + q2, book.values())}""")
            message = messages.get()
            if message["u"] <= last_update_id:
                continue

            if command == ExecutionParams.CMD_SELL:
                update = message["b"]
            else:
                update = message["a"]

            for level in update:
                book[level[0]] = float(level[1])

        self.socket.stop_socket(socket_number)

    def _book_snapshot(self, command: str, symbol: str) -> Tuple[Dict[str, float], int]:

        book = {}
        snapshot = self.client.get_order_book(symbol=symbol, limit=5000)

        if command == ExecutionParams.CMD_SELL:
            snapshot_orders = snapshot["bids"]
        else:
            snapshot_orders = snapshot["asks"]

        for level in snapshot_orders:
            book[level[0]] = float(level[1])
        print(f"""Book snapshot length: {len(book)}""")
        return book, snapshot["lastUpdateId"]

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
