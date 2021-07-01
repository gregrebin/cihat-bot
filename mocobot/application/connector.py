from mocobot.framework.module import Module
from mocobot.framework.events import Event
from mocobot.application.order import Single, Status
from mocobot.application.market import Trade, Interval, Candle
from dataclasses import dataclass, field
from configparser import SectionProxy
from typing import Tuple
from abc import abstractmethod
from typing import Dict, Callable, Type


class Connector(Module):
    ORDER_STATUS_FILLED = "FILLED"
    ORDER_STATUS_CANCELED = "CANCELED"

    def __init__(self, config: SectionProxy,  category: Type, name: str, username: str, password: str):
        super().__init__(config, category, name)
        self.username = username
        self.password = password

    @property
    def events(self) -> Dict[Type, Callable]:
        return {}

    @abstractmethod
    def submit(self, execution_order: Single) -> Tuple[int, float]:
        pass

    @abstractmethod
    def cancel(self, execution_order: Single) -> None:
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
class TradeEvent(Event):
    """ Fires trader.exchange_update """
    name: str
    symbol: str
    trade: Trade


@dataclass
class CandleEvent(Event):
    """ Fires trader.ticker_update """
    name: str
    symbol: str
    interval: Interval
    candle: Candle


@dataclass
class UserEvent(Event):
    """ Fires ui.trades_update """
    uid: str
    status: Status
