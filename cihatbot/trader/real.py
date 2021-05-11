from cihatbot.events import Event
from cihatbot.application.events import (
    ConnectEvent,
    AddEvent,
    DeleteEvent,
    ConnectedEvent,
    AddedEvent,
    DeletedEvent,
    SubmittedEvent,
    FilledEvent,
    CancelledEvent,
    UserEvent,
    TickerEvent,
    ErrorEvent,
    TimerEvent
)
from cihatbot.trader.trader import Trader
from cihatbot.execution_order.execution_order import ExecutionOrder, EmptyExecutionOrder, SingleExecutionOrder, OrderStatus
from cihatbot.connector.connector import Connector, ConnectorException, FailedException
from cihatbot.util.timer import Timer
from configparser import SectionProxy


class RealTrader(Trader):

    log_name = __name__

    def __init__(self, config: SectionProxy, connector: Connector, timer: Timer) -> None:
        super().__init__(config, connector, timer)
        self.execution_order: ExecutionOrder = EmptyExecutionOrder()

    def on_event(self, event: Event) -> None:
        # super().on_event(event)
        if event.is_type(ConnectEvent):
            self.connect(event)
        elif event.is_type(AddEvent):
            self.add_order(event)
        elif event.is_type(DeleteEvent):
            self.delete_order(event)
        elif event.is_type(UserEvent) and event.data["status"] == Connector.ORDER_STATUS_FILLED:
            self.remove_filled(event.data["external_id"])
        elif event.is_type(UserEvent) and event.data["status"] == Connector.ORDER_STATUS_CANCELED:
            self.remove_cancelled(event.data["external_id"])
        elif event.is_type(TickerEvent) or event.is_type(TimerEvent):
            self.submit_next()

    def connect(self, event: Event) -> None:
        user = event.data["user"]
        password = event.data["password"]

        self.log(f"""CONNECT event: {user}""")
        self.connector.connect(user, password)
        self.emit(ConnectedEvent({"user": user}))

    def add_order(self, event: Event) -> None:
        order = event.data["order"]
        mode = event.data["mode"]

        self.log(f"""ADD event: {order}""")
        if mode == "parallel":
            self.execution_order = self.execution_order.add_parallel(order)
        elif mode == "sequent":
            self.execution_order = self.execution_order.add_sequential(order)
        self.emit(AddedEvent({"all": self.execution_order, "single": order}))

    def delete_order(self, event: Event) -> None:
        order_id = event.data["order_id"]

        self.log(f"""DELETE event: {order_id}""")
        self.execution_order = self.execution_order.cancel(order_id=order_id)
        self.emit(DeletedEvent({"all": self.execution_order, "order_id": order_id}))

    def _cancel(self, order: SingleExecutionOrder) -> None:
        if order.status == OrderStatus.SUBMITTED:
            self._call_cancel(order)

    def _call_cancel(self, order: SingleExecutionOrder) -> None:
        try:
            self.connector.cancel(order)
        except ConnectorException as exception:
            self.log(f"""Connector error on cancel: {exception.order} - {exception.message}""")
            self.emit(ErrorEvent({"order": exception.order, "message": exception.message}))

    def submit_next(self) -> None:
        self.execution_order.submit(self._submit)

    def _submit(self, order: SingleExecutionOrder) -> OrderStatus:

        if not (self.timer.is_later_than(order.from_time) and self._call_satisfied(order)):
            return OrderStatus.PENDING

        status = self._call_submit(order)

        if status == OrderStatus.SUBMITTED:
            self.log(f"""Order submitted: {order}""")
            self.emit(SubmittedEvent({"all": self.execution_order, "single": order}))

        return status

    def _call_satisfied(self, order: SingleExecutionOrder) -> bool:

        try:
            return self.connector.satisfied(order)

        except ConnectorException as exception:
            self.log(f"""Connector error on satisfied: {exception.order} - {exception.message}""")
            self.emit(ErrorEvent({"order": exception.order, "message": exception.message}))
            return False

    def _call_submit(self, order: SingleExecutionOrder) -> OrderStatus:

        try:
            order.external_id, order.params.price = self.connector.submit(order)
            print(f"""order price changed: {order.params.price}""")
            return OrderStatus.SUBMITTED

        except FailedException as exception:
            self.log(f"""Order failed: {exception.order} - {exception.message}""")
            return OrderStatus.PENDING

        except ConnectorException as exception:
            self.log(f"""Connector error on submit: {exception.order} - {exception.message}""")
            self.emit(ErrorEvent({"order": exception.order, "message": exception.message}))
            return OrderStatus.REJECTED

    def remove_filled(self, external_id: int) -> None:
        self.execution_order.call(self._signal_filled, external_id=external_id)
        self.execution_order = self.execution_order.remove(external_id=external_id)

    def _signal_filled(self, order: SingleExecutionOrder) -> None:
        self.log(f"""Filled order: {order}""")
        self.emit(FilledEvent({"all": self.execution_order, "single": order}))

    def remove_cancelled(self, external_id: int) -> None:
        self.execution_order.call(self._signal_cancelled, external_id=external_id)
        self.execution_order = self.execution_order.remove(external_id=external_id)

    def _signal_cancelled(self, order: SingleExecutionOrder) -> None:
        self.log(f"""Cancelled order: {order}""")
        self.emit(CancelledEvent({"all": self.execution_order, "single": order}))






