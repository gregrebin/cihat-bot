from cihatbot.utils.execution_order import SingleExecutionOrder, ExecutionConditions, ExecutionParams
from binance.client import Client
from binance.exceptions import BinanceOrderException


class Connector:

    def satisfied(self, execution_order: SingleExecutionOrder) -> bool:
        pass

    def submit(self, execution_order: SingleExecutionOrder) -> int:
        pass

    def is_filled(self, execution_order: SingleExecutionOrder) -> bool:
        pass


class BinanceConnector(Connector):

    def __init__(self, key, secret):
        self.client: Client = Client(api_key=key, api_secret=secret)

    def satisfied(self, execution_order: SingleExecutionOrder) -> bool:

        execution_conditions = execution_order.conditions
        from_time = int(execution_conditions.from_time) * 1000

        binance_time = self.client.get_server_time()["serverTime"]

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

        return binance_order["orderId"]

    def is_filled(self, execution_order: SingleExecutionOrder) -> bool:

        binance_order = self.client.get_order(
            symbol=execution_order.params.symbol,
            orderId=execution_order.order_id
        )

        return binance_order["status"] == self.client.ORDER_STATUS_FILLED


class RejectedOrder(Exception):
    def __init__(self, order: SingleExecutionOrder):
        self.order = order
