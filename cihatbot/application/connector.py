from cihatbot.framework.module import Module
from cihatbot.framework.events import Event
from cihatbot.application.order import SingleExecutionOrder
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
class TradeEvent(Event):
    """ Fires trader.trade """


@dataclass
class CandleEvent(Event):
    """ Fires trader.candle """


@dataclass
class BookEvent(Event):
    """ Fires trader.book """


@dataclass
class TimeEvent(Event):
    """ Fires trader.time """


@dataclass
class SubmittedEvent(Event):
    """ Fires ui.submitted """
    uid: str


@dataclass
class FilledEvent(Event):
    """ Fires ui.filled """
    uid: str


@dataclass
class RejectedEvent(Event):
    """ Fires ui.rejected """
    uid: str
