from cihatbot.logger import Logger
from cihatbot.events import Event
from cihatbot.trader.trader import Trader
from cihatbot.execution_order.execution_order import ExecutionOrder, EmptyExecutionOrder, SingleExecutionOrder
from cihatbot.connector.connector import Connector, ConnectorException
from queue import Queue
from threading import Event as ThreadEvent
from typing import Dict
import logging
import time


class RealTrader(Trader):

    CONNECT_EVENT: str = "CONNECT"
    ADD_ORDER_EVENT: str = "ADD"
    DELETE_ORDER_EVENT: str = "DELETE"

    def __init__(self, config: Dict, queue: Queue, exit_event: ThreadEvent, connector: Connector) -> None:
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
            time.sleep(self.connector.ORDER_DELAY)
            self.remove_filled()
            time.sleep(self.connector.QUERY_DELAY)

    def connect(self, event: Event) -> None:
        user = event.data["user"]
        password = event.data["password"]
        self.logger.log(logging.INFO, f"""CONNECT event: {user}""")
        self.connector.connect(user, password)
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
        self.execution_order = self.execution_order.remove(order_id, self._delete)
        self.emit_event(Event("DELETED", {"all": self.execution_order, "order_id": order_id}))

    def _delete(self, order: SingleExecutionOrder) -> None:
        if order.submitted:
            self._call_cancel(order)

    def _call_cancel(self, order: SingleExecutionOrder) -> None:
        try:
            self.connector.cancel(order)
        except ConnectorException as exception:
            self.emit_event(Event("ERROR", {"order": exception.order, "message": exception.message}))

    def submit_next(self) -> None:
        self.execution_order.submit_next(self._submit)

    def _submit(self, order: SingleExecutionOrder) -> bool:

        if not self._call_satisfied(order):
            return False

        if not self._call_submit(order):
            return False

        self.logger.log(logging.INFO, f"""Order submitted: {order}""")
        self.emit_event(Event("SUBMITTED", {"all": self.execution_order, "single": order}))
        return True

    def _call_satisfied(self, order: SingleExecutionOrder) -> bool:

        try:
            return self.connector.satisfied(order)

        except ConnectorException as exception:
            self.emit_event(Event("ERROR", {"order": exception.order, "message": exception.message}))
            return False

    def _call_submit(self, order: SingleExecutionOrder) -> bool:

        try:
            order.external_id = self.connector.submit(order)
            return True

        except ConnectorException as exception:
            self.emit_event(Event("ERROR", {"order": exception.order, "message": exception.message}))
            return False

    def remove_filled(self) -> None:
        self.execution_order = self.execution_order.remove_filled(self._is_filled)

    def _is_filled(self, order: SingleExecutionOrder) -> bool:

        if not self._call_is_filled(order):
            return False

        self.logger.log(logging.INFO, f"""Order filled: {order}""")
        self.emit_event(Event("FILLED", {"all": self.execution_order, "single": order}))
        return True

    def _call_is_filled(self, order: SingleExecutionOrder) -> bool:

        try:
            return self.connector.is_filled(order)

        except ConnectorException as exception:
            self.emit_event(Event("ERROR", {"order": exception.order, "message": exception.message}))
            return False





