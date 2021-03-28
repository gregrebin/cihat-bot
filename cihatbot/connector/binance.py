from __future__ import annotations
from cihatbot.connector.connector import Connector, ConnectorException
from cihatbot.execution_order.execution_order import SingleExecutionOrder, ExecutionConditions, ExecutionParams
from binance.client import Client
from binance.exceptions import BinanceOrderException, BinanceRequestException, BinanceAPIException
from binance.websockets import BinanceSocketManager
from typing import Callable, Dict


class BinanceConnector(Connector):

    ORDER_DELAY: float = 0.5
    QUERY_DELAY: float = 0.01

    def __init__(self):
        self.client: Client = Client("", "")
        self.socket = BinanceSocketManager(self.client)

    def connect(self, key: str, secret: str) -> None:
        self.client = Client(api_key=key, api_secret=secret)
        self.socket = BinanceSocketManager(self.client)

    def start_listen(self, on_filled: Callable[[int], None], on_canceled: Callable[[int], None]):

        def on_message(message: Dict):
            message_type = message["e"]
            if not message_type == "executionReport":
                return
            order_status = message["X"]
            order_id = message["i"]
            if order_status == "FILLED":
                on_filled(order_id)
            if order_status == "CANCELLED":
                on_canceled(order_id)

        self.socket.start_user_socket(on_message)
        self.socket.daemon = True
        self.socket.start()

    def stop_listen(self):
        self.socket.close()

    def satisfied(self, execution_order: SingleExecutionOrder) -> bool:

        execution_conditions = execution_order.conditions
        from_time = int(execution_conditions.from_time) * 1000

        try:
            binance_time = self.client.get_server_time()["serverTime"]
        except (BinanceRequestException, BinanceAPIException) as exception:
            raise ConnectorException(exception.message, execution_order)

        return binance_time >= from_time

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
