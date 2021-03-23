from cihatbot.logger import Logger
from cihatbot.events import Event
from cihatbot.trader.trader import Trader
from cihatbot.execution_order.execution_order import ExecutionOrder, EmptyExecutionOrder, SingleExecutionOrder
from cihatbot.connector.connector import Connector, RejectedOrder, NonExistentOrder
from configparser import SectionProxy
from queue import Queue
from threading import Event as ThreadEvent
from typing import List
import logging


class RealTrader(Trader):

    CONNECT_EVENT: str = "CONNECT"
    EXECUTE_EVENT: str = "EXECUTE"

    def __init__(self, config: SectionProxy, queue: Queue, exit_event: ThreadEvent, connector: Connector) -> None:
        super().__init__(config, queue, exit_event, connector)

        self.logger: Logger = Logger(__name__, logging.INFO)

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
        user = event.data["user"]
        password = event.data["password"]
        self.logger.log(logging.INFO, f"""CONNECT event: {user}""")
        self.connector.connect(user, password)
        self._set_order(EmptyExecutionOrder())

    def set_execute(self, event: Event) -> None:
        order = event.data["order"]
        self.logger.log(logging.INFO, f"""EXECUTE event: {order}""")
        self._set_order(order)

    def execute(self) -> None:
        try:
            self.execution_order.execute(self._execute_order)
        except RejectedOrder as rejected_order:
            self.logger.log(logging.INFO, f"""Order rejected: {rejected_order}""")
            self.emit_event(Event("REJECTED", {"all": self.execution_order, "single": rejected_order.order}))
            self._set_order(EmptyExecutionOrder())

    def check(self) -> None:
        for order in self.open_orders:
            if self.connector.is_filled(order):
                self.logger.log(logging.INFO, f"""Order filled: {order}""")
                self.execution_order = self.execution_order.remove(order)
                self.open_orders.remove(order)
                self.emit_event(Event("FILLED", {"single_order": order}))

    def _execute_order(self, execution_order: SingleExecutionOrder) -> bool:

        if not self.connector.satisfied(execution_order):
            return False

        order_id = self.connector.submit(execution_order)

        execution_order.order_id = order_id
        self.open_orders.append(execution_order)

        self.logger.log(logging.INFO, f"""Order submitted: {execution_order}""")
        return True

    def _set_order(self, execution_order: ExecutionOrder):
        for order in self.open_orders:
            self.connector.cancel(order)
        self.execution_order = execution_order
        self.open_orders = []





