from cihatbot.connector.connector import Connector, RejectedOrder, NonExistentOrder
from cihatbot.execution_order.execution_order import SingleExecutionOrder, ExecutionConditions, ExecutionParams
from binance.client import Client
from binance.exceptions import BinanceOrderException, BinanceRequestException
import time


class BinanceConnector(Connector):
    ORDER_TIME: float = 3.0
    QUERY_TIME: float = 0.05

    def __init__(self):
        self.client: Client = Client()

    def connect(self, key: str, secret: str) -> None:
        self.client = Client(api_key=key, api_secret=secret)

    def satisfied(self, execution_order: SingleExecutionOrder) -> bool:

        execution_conditions = execution_order.conditions
        from_time = int(execution_conditions.from_time) * 1000

        binance_time = self.client.get_server_time()["serverTime"]

        time.sleep(BinanceConnector.QUERY_TIME)

        return binance_time >= from_time

    def submit(self, execution_order: SingleExecutionOrder) -> int:

        execution_params = execution_order.params

        side = self.client.SIDE_BUY
        if execution_params.command == ExecutionParams.CMD_SELL:
            side = self.client.SIDE_SELL

        try:
            binance_order = self.client.create_order(
                symbol=execution_params.symbol,
                quantity=execution_params.quantity,
                price=execution_params.price,
                side=side,
                type=self.client.ORDER_TYPE_LIMIT,
                timeInForce=self.client.TIME_IN_FORCE_GTC
            )
        except BinanceOrderException:
            raise RejectedOrder(execution_order)

        time.sleep(BinanceConnector.ORDER_TIME)

        return binance_order["orderId"]

    def is_filled(self, execution_order: SingleExecutionOrder) -> bool:

        try:
            binance_order = self.client.get_order(
                symbol=execution_order.params.symbol,
                orderId=execution_order.order_id
            )
        except BinanceRequestException:
            raise NonExistentOrder(execution_order)

        time.sleep(BinanceConnector.QUERY_TIME)

        return binance_order["status"] == self.client.ORDER_STATUS_FILLED

    def cancel(self, execution_order: SingleExecutionOrder) -> None:

        try:
            self.client.cancel_order(
                symbol=execution_order.params.symbol,
                orderId=execution_order.order_id
            )
        except BinanceRequestException:
            raise NonExistentOrder(execution_order)

        time.sleep(BinanceConnector.QUERY_TIME)
