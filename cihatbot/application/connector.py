from cihatbot.framework.module import Module
from cihatbot.framework.events import Event
from cihatbot.application.order import SingleExecutionOrder, Status
from dataclasses import dataclass
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


@dataclass
class ExchangeEvent(Event):
    """ Fires trader.exchange_update """


@dataclass
class TickerEvent(Event):
    """ Fires trader.ticker_update """


@dataclass
class UserEvent(Event):
    """ Fires ui.trades_update """
    uid: str
    status: Status
