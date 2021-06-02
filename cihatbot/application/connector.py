from cihatbot.framework.module import Module
from cihatbot.application.order import SingleExecutionOrder
from typing import Tuple


class Connector(Module):

    ORDER_STATUS_FILLED = "FILLED"
    ORDER_STATUS_CANCELED = "CANCELED"

    def __init__(self):
        super().__init__({})

    def connect(self, key: str, secret: str) -> None:
        pass

    def satisfied(self, execution_order: SingleExecutionOrder) -> bool:
        pass

    def submit(self, execution_order: SingleExecutionOrder) -> Tuple[int, float]:
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
