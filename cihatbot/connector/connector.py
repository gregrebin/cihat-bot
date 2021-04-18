from cihatbot.events import Event, EventEmitter, EventListener
from cihatbot.execution_order.execution_order import SingleExecutionOrder, ExecutionConditions, ExecutionParams
from typing import Callable


class Connector:

    ORDER_STATUS_FILLED = "FILLED"
    ORDER_STATUS_CANCELED = "CANCELED"

    def __init__(self):
        self.emitter: EventEmitter = EventEmitter()

    def add_listener(self, listener: EventListener):
        self.emitter.add_listener(listener)

    def emit(self, event: Event):
        self.emitter.emit(event)

    def connect(self, key: str, secret: str) -> None:
        pass

    def start_listen(self):
        pass

    def stop_listen(self):
        pass

    def satisfied(self, execution_order: SingleExecutionOrder) -> bool:
        pass

    def submit(self, execution_order: SingleExecutionOrder) -> int:
        pass

    def is_filled(self, execution_order: SingleExecutionOrder) -> bool:
        pass

    def cancel(self, execution_order: SingleExecutionOrder) -> None:
        pass


class ConnectorException(Exception):
    def __init__(self, message: str, order: SingleExecutionOrder):
        self.message = message
        self.order = order


class FailedException(ConnectorException):
    pass
