from cihatbot.events import Event
from cihatbot.module import Module
from cihatbot.utils.execution_order import \
    ExecutionOrder, EmptyExecutionOrder, SingleExecutionOrder, ExecutionParams
from binance.client import Client
from typing import List
from time import sleep
from queue import Queue
from configparser import SectionProxy
from threading import Event as ThreadEvent


class Binance(Module):

    ORDER_TIME = 0.5
    QUERY_TIME = 0.005
    CONNECT_EVENT = "CONNECT"
    EXECUTE_EVENT = "EXECUTE"

    def __init__(self, config: SectionProxy, queue: Queue, exit_event: ThreadEvent):
        super().__init__(config, queue, exit_event)
        self.client: Client = Client(api_key=config["api"], api_secret=config["secret"])
        self.execution_order: ExecutionOrder = EmptyExecutionOrder()
        self.open_orders: List[SingleExecutionOrder] = []

    def loop(self, event: Event) -> None:
        if event.name == Binance.CONNECT_EVENT:
            self.connect(event)
        elif event.name == Binance.EXECUTE_EVENT:
            self.set_execute(event)
        else:
            self.execute()
            self.check()

    def connect(self, event: Event):
        self.client = Client(api_key=event.data["user"], api_secret=event.data["password"])

    def set_execute(self, event: Event):
        self.open_orders = []
        self.execution_order = event.data["order"]

    def execute(self):
        self.execution_order.execute(self._execute_order)

    def check(self):
        for order in self.open_orders:
            self._check_order(order)

    def _execute_order(self, execution_order: SingleExecutionOrder):

        execution_params = execution_order.params

        side = self.client.SIDE_BUY
        if execution_params.command == ExecutionParams.CMD_SELL:
            side = self.client.SIDE_SELL

        binance_order = self.client.create_order(
            symbol=execution_params.symbol,
            quantity=execution_params.quantity,
            price=execution_params.price,
            side=side,
            type=self.client.ORDER_TYPE_LIMIT,
            timeInForce=self.client.TIME_IN_FORCE_GTC
        )

        execution_order.order_id = binance_order["orderId"]
        self.open_orders.append(execution_order)

        sleep(Binance.ORDER_TIME)

    def _check_order(self, execution_order: SingleExecutionOrder):

        binance_order = self.client.get_order(
            symbol=execution_order.params.symbol,
            orderId=execution_order.order_id
        )

        if binance_order["status"] == self.client.ORDER_STATUS_FILLED:
            self.execution_order.remove(execution_order)

        sleep(Binance.QUERY_TIME)





