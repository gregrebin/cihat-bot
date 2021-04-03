from __future__ import annotations
from cihatbot.events import UserEvent, TickerEvent
from cihatbot.connector.connector import Connector, ConnectorException
from cihatbot.execution_order.execution_order import SingleExecutionOrder, ExecutionConditions, ExecutionParams
from binance.client import Client
from binance.exceptions import BinanceOrderException, BinanceRequestException, BinanceAPIException
from binance.websockets import BinanceSocketManager
from typing import Callable, Dict, List


class BinanceConnector(Connector):

    ORDER_DELAY: float = 0.5
    QUERY_DELAY: float = 0.01

    def __init__(self):
        super().__init__()
        self.client: Client = Client("", "")
        self.socket = BinanceSocketManager(self.client)
        self.connected: bool = False
        self.time: int = 0

    def connect(self, key: str, secret: str) -> None:
        self.client = Client(api_key=key, api_secret=secret)
        self.socket = BinanceSocketManager(self.client)
        self.connected = True

    def start_listen(self):

        if not self.connected:
            return

        def user_handler(message: Dict):
            message_type = message["e"]
            if not message_type == "executionReport":
                return
            order_status = message["X"]
            order_id = message["i"]
            self.emit(UserEvent({"external_id": order_id, "status": order_status}))

        def ticker_handler(message: List[Dict]):
            for ticker in message:
                self._ticker_handler(ticker)
            self.emit(TickerEvent({}))

        self.socket.start_user_socket(user_handler)
        self.socket.start_miniticker_socket(ticker_handler)
        self.socket.daemon = True
        self.socket.start()

    def _ticker_handler(self, ticker: Dict):
        message_type = ticker["e"]
        if not message_type == "24hrMiniTicker":
            return
        time = ticker["E"]
        if time > self.time:
            self.time = time

    def stop_listen(self):
        self.socket.close()

    def satisfied(self, execution_order: SingleExecutionOrder) -> bool:

        execution_conditions = execution_order.conditions
        from_time = int(execution_conditions.from_time) * 1000

        return self.time >= from_time

    def submit(self, execution_order: SingleExecutionOrder) -> int:

        execution_params = execution_order.params

        side = self.client.SIDE_BUY
        if execution_params.command == ExecutionParams.CMD_SELL:
            side = self.client.SIDE_SELL

        try:
            binance_order = self.client.create_order(
                newClientOrderId=execution_order.order_id,
                symbol=execution_params.symbol,
                quantity=execution_params.quantity,
                price=execution_params.price,
                side=side,
                type=self.client.ORDER_TYPE_LIMIT,
                timeInForce=self.client.TIME_IN_FORCE_GTC
            )
        except (BinanceRequestException, BinanceOrderException, BinanceAPIException) as exception:
            raise ConnectorException(exception.message, execution_order)

        return binance_order["orderId"]

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
