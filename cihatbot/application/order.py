from __future__ import annotations
from threading import Lock
from typing import List, Callable, Dict, Tuple
from uuid import uuid4, UUID
from enum import Enum, auto
from dataclasses import dataclass, field, replace
from abc import ABC, abstractmethod
from sly import Lexer

def new_uid():
    return uuid4().hex


class Status(Enum):
    NEW = auto()
    SUBMITTED = auto()
    CANCELLED = auto()
    FILLED = auto()
    REJECTED = auto()


class Command(Enum):
    BUY = auto()
    SELL = auto()


class Mode(Enum):
    PARALLEL = auto()
    SEQUENT = auto()


@dataclass(frozen=True)
class Order(ABC):

    status: Status = Status.NEW
    uid: str = field(default_factory=new_uid)

    @abstractmethod
    def add(self, order: Order, mode: Mode) -> Order:
        pass

    @abstractmethod
    def get(self, pending: bool = True) -> List[Order]:
        pass

    @abstractmethod
    def update(self, uid: str, status: Status) -> Order:
        pass

    def _add(self, order: Order, mode: Mode) -> Order:
        orders = self._add_term(mode) + order._add_term(mode)
        return Multiple(mode=mode, orders=orders)

    def _add_term(self, mode: Mode) -> Tuple[Order, ...]:
        return self,


@dataclass(frozen=True)
class Empty(Order):

    def add(self, order: Order, mode: Mode) -> Order:
        return order

    def get(self, pending: bool = True) -> List[Order]:
        return []

    def update(self, uid: str, status: Status) -> Order:
        return self


@dataclass(frozen=True)
class Single(Order):

    # TODO: implement multiple prices, think better about conditions

    eid: str = ""
    exchange: str = ""
    command: Command = Command.BUY
    symbol: str = ""
    quote: float = 0
    base: float = 0
    price: float = 0
    conditions: Dict[str, float] = field(default_factory=dict)

    def add(self, order: Order, mode: Mode) -> Order:
        return super()._add(order, mode)

    def get(self, pending: bool = True) -> List[Order]:
        if pending and self.status is not Status.NEW:
            return []
        return [self]

    def update(self, uid: str, status: Status) -> Order:
        if self.uid == uid:
            return replace(self, status=status)
        else:
            return self


@dataclass(frozen=True)
class Multiple(Order):

    mode: Mode = Mode.PARALLEL
    orders: Tuple[Order, ...] = field(default_factory=tuple)

    def add(self, order: Order, mode: Mode) -> Order:
        return super()._add(order, mode)

    def _add_term(self, mode: Mode) -> Tuple[Order, ...]:
        if self.mode is mode:
            return self.orders
        else:
            return self,

    def get(self, pending: bool = True) -> List[Order]:
        if pending and self.status is not Status.NEW:
            return []
        result = []
        for order in self.orders:
            orders = order.get(pending)
            result += orders
            if self.mode is Mode.SEQUENT and pending and orders:
                break
        return result

    def update(self, uid: str, status: Status) -> Order:
        if self.uid == uid:
            return replace(self, status=status)
        else:
            orders = tuple(order.update(uid, status) for order in self.orders)
            return replace(self, orders=orders)


# Parser formal grammar:
# ---------------
# order ::= <empty> | <single> | <multiple>
#   empty ::= ""
#   single ::= <command> <quote> <symbol> in <exchange> at <price> | <command> <symbol> in <exchange> at <price> for <base>  (ex. buy 5 BTCUSDT in Binance at 20000 / buy BTCUSDT in Binance at 20000 for 1000)
#       command ::= buy | sell
#       quote ::= <decimal>
#       symbol ::= <string>
#       exchange ::= <string>
#       price ::= <decimal>
#       base ::= <string>
#   multiple ::= [<mode> <orders>]
#       mode ::= parallel | sequent
#       orders ::= <order> | <order>, <orders>

# https://sly.readthedocs.io/en/latest/sly.html
# https://yahel-oppenheimer.medium.com/create-your-own-scripting-language-in-python-with-sly-7b864e762e07
# https://www.rexegg.com/regex-quickstart.html

# noinspection PyUnresolvedReferences,PyUnboundLocalVariable
class OrderLexer(Lexer):

    tokens = {COMMAND, MODE, IN, AT, FOR, DECIMAL, STRING}
    literals = {","}

    ignore = r" \t"

    IN = r"in"
    AT = r"at"
    FOR = r"for"
    COMMAND = r"(buy|sell)"
    MODE = r"(parallel|sequent)"
    DECIMAL = "\d+\.?\d*"
    STRING = "\w+"

