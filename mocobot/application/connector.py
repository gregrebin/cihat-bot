from mocobot.framework.module import Module
from mocobot.framework.events import Event
from mocobot.application.order import SingleExecutionOrder, Status
from dataclasses import dataclass, field
from configparser import SectionProxy
from typing import Tuple
from abc import abstractmethod
from typing import Dict, Callable


class Connector(Module):
    ORDER_STATUS_FILLED = "FILLED"
    ORDER_STATUS_CANCELED = "CANCELED"

    log_name = __name__

    def __init__(self, config: SectionProxy, username: str, password: str):
        super().__init__(config)
        self.username = username
        self.password = password
        self.events: Dict[str, Callable] = {}

    @abstractmethod
    def submit(self, execution_order: SingleExecutionOrder) -> Tuple[int, float]:
        pass

    @abstractmethod
    def cancel(self, execution_order: SingleExecutionOrder) -> None:
        pass


# class ConnectorException(Exception):
#     def __init__(self, message: str, order: SingleExecutionOrder):
#         self.message = message
#         self.order = order
#
#
# class FailedException(ConnectorException):
#     pass


@dataclass
class ExchangeEvent(Event):
    """ Fires trader.exchange_update """
    name: str = field(init=False, default="ExchangeEvent")


@dataclass
class TickerEvent(Event):
    """ Fires trader.ticker_update """
    name: str = field(init=False, default="TickerEvent")


@dataclass
class UserEvent(Event):
    """ Fires ui.trades_update """
    uid: str
    status: Status
    name: str = field(init=False, default="UserEvent")
