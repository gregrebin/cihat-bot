from cihatbot.logger import Logger
from cihatbot.events import Event
from cihatbot.trader.trader import Trader
from cihatbot.execution_order.execution_order import ExecutionOrder, EmptyExecutionOrder, SingleExecutionOrder
from cihatbot.connector.connector import Connector, RejectedOrder, NonExistentOrder
from configparser import SectionProxy
from queue import Queue
from threading import Event as ThreadEvent
import logging


class RealTrader(Trader):

    CONNECT_EVENT: str = "CONNECT"
    ADD_ORDER_EVENT: str = "ADD_ORDER"
    DELETE_ORDER_EVENT: str = "DELETE_ORDER"

    def __init__(self, config: SectionProxy, queue: Queue, exit_event: ThreadEvent, connector: Connector) -> None:
        super().__init__(config, queue, exit_event, connector)

        self.logger: Logger = Logger(__name__, logging.INFO)
        self.execution_order: ExecutionOrder = EmptyExecutionOrder()

        if "user" in config and "password" in config:
            self.connector.connect(self.config["user"], self.config["password"])

    def loop(self, event: Event) -> None:
        if event.name == RealTrader.CONNECT_EVENT:
            self.connect(event)
        elif event.name == RealTrader.ADD_ORDER_EVENT:
            self.add_order(event)
        elif event.name == RealTrader.DELETE_ORDER_EVENT:
            self.delete_order(event)
        else:
            self.submit_next()
            self.remove_filled()

    def connect(self, event: Event) -> None:
        user = event.data["user"]
        password = event.data["password"]
        self.logger.log(logging.INFO, f"""CONNECT event: {user}""")
        self.connector.connect(user, password)
        self.logger.log(logging.INFO, f"""CONNECTED event: {user}""")

    def add_order(self, event: Event) -> None:
        order = event.data["order"]
        mode = event.data["mode"]
        self.logger.log(logging.INFO, f"""ADD event: {order}""")
        if mode == "parallel":
            self.execution_order.add_parallel(order)
        elif mode == "sequent":
            self.execution_order.add_sequential(order)
        self.emit_event(Event("ADDED", {"all": self.execution_order, "single": order}))

    def delete_order(self, event: Event) -> None:
        order_id = event.data["order_id"]
        self.logger.log(logging.INFO, f"""DELETE event: {order_id}""")
        self.execution_order.remove(order_id, self._delete)
        self.emit_event(Event("DELETED", {"all": self.execution_order, "order_id": order_id}))

    def _delete(self, execution_order: SingleExecutionOrder) -> None:
        if execution_order.submitted:
            self.connector.cancel(execution_order)

    def submit_next(self) -> None:
        self.execution_order.submit_next(self._submit)

    def _submit(self, order: SingleExecutionOrder) -> bool:

        if not self.connector.satisfied(order):
            return False

        external_id = self.connector.submit(order)
        order.external_id = external_id

        self.logger.log(logging.INFO, f"""Order submitted: {order}""")
        self.emit_event(Event("SUBMITTED", {"all": self.execution_order, "single": order}))
        return True

    def remove_filled(self) -> None:
        self.execution_order = self.execution_order.remove_filled(self._is_filled)

    def _is_filled(self, order: SingleExecutionOrder) -> bool:

        if self.connector.is_filled(order):
            self.logger.log(logging.INFO, f"""Order filled: {order}""")
            self.emit_event(Event("FILLED", {"all": self.execution_order, "single": order}))
            return True

        else:
            return False





