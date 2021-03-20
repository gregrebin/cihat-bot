from cihatbot.events import Event
from cihatbot.trader.trader import Trader
from cihatbot.execution_order.execution_order import ExecutionOrder, EmptyExecutionOrder, SingleExecutionOrder
from cihatbot.connector.connector import Connector, RejectedOrder
from configparser import SectionProxy
from queue import Queue
from threading import Event as ThreadEvent
from typing import List


class RealTrader(Trader):

    CONNECT_EVENT: str = "CONNECT"
    EXECUTE_EVENT: str = "EXECUTE"

    def __init__(self, config: SectionProxy, queue: Queue, exit_event: ThreadEvent, connector: Connector) -> None:
        super().__init__(config, queue, exit_event, connector)

        self.connector.connect(self.config["user"], self.config["password"])

        self.execution_order: ExecutionOrder = EmptyExecutionOrder()
        self.open_orders: List[SingleExecutionOrder] = []

    def loop(self, event: Event) -> None:
        if event.name == RealTrader.CONNECT_EVENT:
            self.connect(event)
        elif event.name == RealTrader.EXECUTE_EVENT:
            self.set_execute(event)
        else:
            self.execute()
            self.check()

    def connect(self, event: Event) -> None:
        self.connector.connect(event.data["user"], event.data["password"])
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

        if not self.connector.satisfied(execution_order):
            return False

        order_id = self.connector.submit(execution_order)

        execution_order.order_id = order_id
        self.open_orders.append(execution_order)

        return True

    def _check_order(self, execution_order: SingleExecutionOrder) -> bool:

        filled = self.connector.is_filled(execution_order)
        if filled:
            self.execution_order.remove(execution_order)

        return filled

    def _clean(self):
        self.execution_order = EmptyExecutionOrder()
        self.open_orders = []





