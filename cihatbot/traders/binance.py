from cihatbot.events import Event
from cihatbot.module import Module
from cihatbot.utils.execution_order import \
    ExecutionOrder, EmptyExecutionOrder, SingleExecutionOrder, ExecutionParams, ExecutionConditions
from binance.client import Client
from binance.exceptions import BinanceOrderException
from typing import List
from time import sleep, time
from queue import Queue
from configparser import SectionProxy
from threading import Event as ThreadEvent


class Binance(Module):

    ORDER_TIME: float = 0.5
    QUERY_TIME: float = 0.005
    CONNECT_EVENT: str = "CONNECT"
    EXECUTE_EVENT: str = "EXECUTE"

    def __init__(self, config: SectionProxy, queue: Queue, exit_event: ThreadEvent) -> None:
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

    def connect(self, event: Event) -> None:
        self.client = Client(api_key=event.data["user"], api_secret=event.data["password"])
        self._clean()

    def set_execute(self, event: Event) -> None:
        self.execution_order = event.data["order"]
        self.open_orders = []

    def execute(self) -> None:
        try:
            self.execution_order.execute(self._execute_order)
        except RejectedOrder as rejected_order:
            self.emit_event(Event("REJECTED", {"all": self.execution_order, "single": rejected_order.order}))
            self._clean()

    def check(self) -> None:
        for order in self.open_orders:
            filled = self._check_order(order)
            if filled:
                self.emit_event(Event("FILLED", {"single_order": order}))

    def _execute_order(self, execution_order: SingleExecutionOrder) -> bool:

        execution_params = execution_order.params
        execution_conditions = execution_order.conditions

        if not self._satisfies_conditions(execution_conditions):
            return False

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

        execution_order.order_id = binance_order["orderId"]
        self.open_orders.append(execution_order)

        sleep(Binance.ORDER_TIME)
        return True

    def _satisfies_conditions(self, execution_conditions: ExecutionConditions) -> bool:
        return time() >= execution_conditions.from_time

    def _check_order(self, execution_order: SingleExecutionOrder) -> bool:

        binance_order = self.client.get_order(
            symbol=execution_order.params.symbol,
            orderId=execution_order.order_id
        )

        filled = binance_order["status"] == self.client.ORDER_STATUS_FILLED
        if filled:
            self.execution_order.remove(execution_order)

        sleep(Binance.QUERY_TIME)
        return filled

    def _clean(self):
        self.execution_order = EmptyExecutionOrder()
        self.open_orders = []


class RejectedOrder(Exception):
    def __init__(self, order: SingleExecutionOrder):
        self.order = order




