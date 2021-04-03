from cihatbot.logger import Logger
from cihatbot.events import Event
from cihatbot.trader.trader import Trader
from cihatbot.execution_order.execution_order import ExecutionOrder, EmptyExecutionOrder, SingleExecutionOrder, OrderStatus
from cihatbot.connector.connector import Connector, ConnectorException
from queue import Queue
from threading import Lock, Event as ThreadEvent
from typing import Dict
import logging


class RealTrader(Trader):

    CONNECT_EVENT: str = "CONNECT"
    ADD_ORDER_EVENT: str = "ADD"
    DELETE_ORDER_EVENT: str = "DELETE"

    def __init__(self, config: Dict, queue: Queue, exit_event: ThreadEvent, connector: Connector) -> None:
        super().__init__(config, queue, exit_event, connector)

        self.logger: Logger = Logger(__name__, logging.INFO)
        self.execution_order: ExecutionOrder = EmptyExecutionOrder()
        self.execution_lock: Lock = Lock()

    def loop(self, event: Event) -> None:
        if event.name == RealTrader.CONNECT_EVENT:
            self.connect(event)
        elif event.name == RealTrader.ADD_ORDER_EVENT:
            self.add_order(event)
        elif event.name == RealTrader.DELETE_ORDER_EVENT:
            self.delete_order(event)

    def post_run(self):
        self.connector.stop_listen()

    def connect(self, event: Event) -> None:
        user = event.data["user"]
        password = event.data["password"]

        self.logger.log(logging.INFO, f"""CONNECT event: {user}""")
        self.connector.connect(user, password)
        self.connector.start_listen(self.remove_filled, self.remove_cancelled, self.submit_next)
        self.emit_event(Event("CONNECTED", {"user": user}))

    def add_order(self, event: Event) -> None:
        order = event.data["order"]
        mode = event.data["mode"]

        self.logger.log(logging.INFO, f"""ADD event: {order}""")
        if mode == "parallel":
            self.execution_order = self.execution_order.add_parallel(order)
        elif mode == "sequent":
            self.execution_order = self.execution_order.add_sequential(order)
        self.emit_event(Event("ADDED", {"all": self.execution_order, "single": order}))

    def delete_order(self, event: Event) -> None:
        order_id = event.data["order_id"]

        self.logger.log(logging.INFO, f"""DELETE event: {order_id}""")
        self.execution_order = self.execution_order.cancel(order_id=order_id)
        self.emit_event(Event("DELETED", {"all": self.execution_order, "order_id": order_id}))

    def _cancel(self, order: SingleExecutionOrder) -> None:
        if order.status == OrderStatus.SUBMITTED:
            self._call_cancel(order)

    def _call_cancel(self, order: SingleExecutionOrder) -> None:
        try:
            self.connector.cancel(order)
        except ConnectorException as exception:
            self.logger.log(logging.INFO, f"""Connector error on cancel: {exception.order} - {exception.message}""")
            self.emit_event(Event("ERROR", {"order": exception.order, "message": exception.message}))

    def submit_next(self) -> None:
        self.execution_order.submit(self._submit)

    def _submit(self, order: SingleExecutionOrder) -> OrderStatus:

        if not self._call_satisfied(order):
            return OrderStatus.PENDING

        if not self._call_submit(order):
            return OrderStatus.REJECTED

        self.logger.log(logging.INFO, f"""Order submitted: {order}""")
        self.emit_event(Event("SUBMITTED", {"all": self.execution_order, "single": order}))
        return OrderStatus.SUBMITTED

    def _call_satisfied(self, order: SingleExecutionOrder) -> bool:

        try:
            return self.connector.satisfied(order)

        except ConnectorException as exception:
            self.logger.log(logging.INFO, f"""Connector error on satisfied: {exception.order} - {exception.message}""")
            self.emit_event(Event("ERROR", {"order": exception.order, "message": exception.message}))
            return False

    def _call_submit(self, order: SingleExecutionOrder) -> bool:

        try:
            order.external_id = self.connector.submit(order)
            return True

        except ConnectorException as exception:
            self.logger.log(logging.INFO, f"""Connector error on submit: {exception.order} - {exception.message}""")
            self.emit_event(Event("ERROR", {"order": exception.order, "message": exception.message}))
            return False

    def remove_filled(self, external_id: int) -> None:
        self.execution_order.call(self._signal_filled, external_id=external_id)
        self.execution_order = self.execution_order.remove(external_id=external_id)

    def _signal_filled(self, order: SingleExecutionOrder) -> None:
        self.logger.log(logging.INFO, f"""Filled order: {order}""")
        self.emit_event(Event("FILLED", {"all": self.execution_order, "single": order}))

    def remove_cancelled(self, external_id: int) -> None:
        self.execution_order.call(self._signal_cancelled, external_id=external_id)
        self.execution_order = self.execution_order.remove(external_id=external_id)

    def _signal_cancelled(self, order: SingleExecutionOrder) -> None:
        self.logger.log(logging.INFO, f"""Cancelled order: {order}""")
        self.emit_event(Event("CANCELLED", {"all": self.execution_order, "single": order}))






