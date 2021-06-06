from cihatbot.framework.module import Module
from cihatbot.framework.events import Event
from cihatbot.application.order import SingleExecutionOrder, Status
from dataclasses import dataclass
from configparser import SectionProxy
from typing import Tuple
from abc import abstractmethod


class Connector(Module):
    ORDER_STATUS_FILLED = "FILLED"
    ORDER_STATUS_CANCELED = "CANCELED"

    log_name = __name__

    def __init__(self, config: SectionProxy, username: str, password: str):
        super().__init__(config)
        self.username = username
        self.password = password

    @abstractmethod
    def submit(self, execution_order: SingleExecutionOrder) -> Tuple[int, float]:
        pass

    @abstractmethod
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
