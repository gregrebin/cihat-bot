from cihatbot.execution_order.execution_order import SingleExecutionOrder, ExecutionConditions, ExecutionParams
from typing import Callable


class Connector:

    ORDER_DELAY: float = 0.0
    QUERY_DELAY: float = 0.0

    def connect(self, key: str, secret: str) -> None:
        pass

    def start_listen(self, on_filled: Callable[[int], None], on_canceled: Callable[[int], None]):
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
