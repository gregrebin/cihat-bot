from cihatbot.events import Event
from cihatbot.module import Module
from cihatbot.utils.execution_order import \
    ExecutionOrder, EmptyExecutionOrder, SingleExecutionOrder, MultipleExecutionOrder, ParallelExecutionOrder, SequentExecutionOrder
from binance.client import Client
from typing import List
from time import sleep
from queue import Queue, Empty


class Binance(Module):

    ORDER_TIME = 0.5
    QUERY_TIME = 0.005
    CONNECT_EVENT = "CONNECT"
    EXECUTE_EVENT = "EXECUTE"

    def __init__(self, config, queue: Queue):
        super().__init__(config, queue)
        self.client: Client = Client(api_key=config["api"], api_secret=config["secret"])
        self.execution_order: ExecutionOrder = ExecutionOrder("empty")
        self.open_orders: List[SingleExecutionOrder] = []

    def run(self) -> None:
        while True:
            try:
                event = self.queue.get(block=False)
            except Empty:
                event = None
            self.loop(event)

    def loop(self, event: Event) -> None:
        if event.name == Binance.CONNECT_EVENT:
            self.connect(event)
        elif event.name == Binance.EXECUTE_EVENT:
            self.execute(event)
        else:
            self.submit()
            self.check()

    def connect(self, event: Event):
        self.client = Client(api_key=event.data["user"], api_secret=event.data["password"])

    def execute(self, event: Event):
        self.open_orders = []
        self.execution_order = event.data["order"]

    def submit(self):
        self._submit_order(self.execution_order)

    def check(self):
        for order in self.open_orders:
            self._check_order(order)

    def _submit_order(self, execution_order: ExecutionOrder):

        if isinstance(execution_order, SingleExecutionOrder):
            self._exec_submit_order(execution_order)

        elif isinstance(execution_order, ParallelExecutionOrder):
            for order in execution_order.orders:
                self._submit_order(order)

        elif isinstance(execution_order, SequentExecutionOrder):
            self._submit_order(execution_order.orders[0])

    def _exec_submit_order(self, execution_order: SingleExecutionOrder):

        if execution_order in self.open_orders:
            return

        side = self.client.SIDE_BUY
        if execution_order.command == ExecutionOrder.CMD_SELL:
            side = self.client.SIDE_SELL

        binance_order = self.client.create_order(
            symbol=execution_order.symbol,
            quantity=execution_order.quantity,
            price=execution_order.price,
            side=side,
            type=self.client.ORDER_TYPE_LIMIT,
            timeInForce=self.client.TIME_IN_FORCE_GTC
        )

        execution_order.order_id = binance_order["orderId"]
        self.open_orders.append(execution_order)

        sleep(Binance.ORDER_TIME)

    def _check_order(self, execution_order: SingleExecutionOrder):

        binance_order = self.client.get_order(
            symbol=execution_order.symbol,
            orderId=execution_order.order_id
        )

        if binance_order["status"] == self.client.ORDER_STATUS_FILLED:
            self._fill_order(execution_order)

        sleep(Binance.QUERY_TIME)

    def _fill_order(self, execution_order: SingleExecutionOrder):

        if isinstance(self.execution_order, SingleExecutionOrder) and self.execution_order == execution_order:
            self.execution_order = EmptyExecutionOrder()

        elif isinstance(self.execution_order, MultipleExecutionOrder):
            self.execution_order.remove_order(execution_order)

        self.open_orders.remove(execution_order)




