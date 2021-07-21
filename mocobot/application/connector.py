from __future__ import annotations
from mocobot.framework.module import Module
from mocobot.framework.events import Event
from mocobot.application.order import Single, Status
from mocobot.application.market import Interval, Candle
from dataclasses import dataclass, field
from configparser import SectionProxy
from typing import Tuple
from abc import abstractmethod
from typing import Dict, Callable, Type


class Connector(Module):
    ORDER_STATUS_FILLED = "FILLED"
    ORDER_STATUS_CANCELED = "CANCELED"

    def __init__(self, config: SectionProxy,  category: Type, name: str, username: str = None, password: str = None):
        super().__init__(config, category, name)
        if (not username and "username" not in self.config) or (not password and "password" not in self.config):
            raise ConnectorException("missing username or password")
        self.username = username if username else self.config["username"]
        self.password = password if password else self.config["password"]

    @property
    def events(self) -> Dict[Type, Callable]:
        return {}

    @property
    @abstractmethod
    def exchange(self) -> str:
        pass

    @abstractmethod
    def start_candles(self, symbol: str, interval: Interval) -> None:
        pass

    @abstractmethod
    def submit(self, order: Single) -> Recipe:
        pass

    @abstractmethod
    def cancel(self, order: Single) -> Recipe:
        pass


class ConnectorException(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


@dataclass
class Recipe:
    eid: str
    status: Status


# class FailedException(ConnectorException):
#     pass


@dataclass
class CandleEvent(Event):
    """ Fires trader.ticker_update """
    exchange: str
    symbol: str
    interval: Interval
    candle: Candle


@dataclass
class UserEvent(Event):
    """ Fires ui.trades_update """
    uid: str
    eid: str
    status: Status
