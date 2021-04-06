from __future__ import annotations
from cihatbot.events import UserEvent, TickerEvent
from cihatbot.connector.connector import Connector, ConnectorException
from cihatbot.execution_order.execution_order import SingleExecutionOrder, ExecutionConditions, ExecutionParams
from binance.client import Client
from binance.exceptions import BinanceOrderException, BinanceRequestException, BinanceAPIException
from binance.websockets import BinanceSocketManager
from typing import Callable, Dict, List


class BinanceConnector(Connector):

    BINANCE_ORDER_STATUS_FILLED = "FILLED"
    BINANCE_ORDER_STATUS_CANCELED = "CANCELED"

    def __init__(self):

        super().__init__()
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
