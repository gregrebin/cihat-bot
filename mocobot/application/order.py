from __future__ import annotations
from threading import Lock
from typing import List, Callable, Dict, Tuple
from uuid import uuid4, UUID
from enum import Enum, auto
from dataclasses import dataclass, field, replace
from abc import ABC, abstractmethod
from sly import Lexer, Parser


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
#   multiple ::= [<mode> <orders>] (ex. [parallel buy 5 BTCUSDT in Binance at 30000, buy ETHUSDT in Coinbase at 2000 for 1000])
#       mode ::= parallel | sequent
#       orders ::= <order> | <order>, <orders>


# noinspection PyUnresolvedReferences,PyUnboundLocalVariable,PyPep8Naming,PyRedeclaration,PyMethodMayBeStatic
class OrderLexer(Lexer):

    tokens = {COMMAND, MODE, IN, AT, FOR, COMMA, LBRACKET, RBRACKET, DECIMAL, STRING}

    ignore = r" \t"

    COMMAND = r"(buy|sell)"
    MODE = r"(parallel|sequent)"
    IN = r"in"
    AT = r"at"
    FOR = r"for"
    COMMA = ","
    LBRACKET = r"\["
    RBRACKET = r"\]"
    DECIMAL = r"\d+\.?\d*"
    STRING = r"\w+"

    def DECIMAL(self, t):
        t.value = float(t.value)
        return t


# noinspection PyUnresolvedReferences
class OrderParser(Parser):

    tokens = OrderLexer.tokens

    @_('single')
    def order(self, p):
        return p.single

    @_('multiple')
    def order(self, p):
        return p.multiple

    @_("LBRACKET MODE orders RBRACKET")
    def multiple(self, p):
        return Multiple(mode=p.MODE, orders=p.orders)

    @_("order COMMA orders")
    def orders(self, p):
        return (p.order,) + p.orders

    @_("order")
    def orders(self, p):
        return p.order,

    @_('COMMAND quote symbol IN exchange AT price')
    def single(self, p):
        return Single(command=p.COMMAND, quote=p.quote, symbol=p.symbol, exchange=p.exchange, price=p.price)

    @_('COMMAND symbol IN exchange AT price FOR base')
    def single(self, p):
        return Single(command=p.COMMAND, symbol=p.symbol, exchange=p.exchange, price=p.price, base=p.base)

    @_('DECIMAL')
    def quote(self, p):
        return p.DECIMAL

    @_('STRING')
    def symbol(self, p):
        return p.STRING

    @_('STRING')
    def exchange(self, p):
        return p.STRING

    @_('DECIMAL')
    def price(self, p):
        return p.DECIMAL

    @_('DECIMAL')
    def base(self, p):
        return p.DECIMAL


def parse(order: str) -> Order:
    lexer = OrderLexer()
    parser = OrderParser()
    tokens = lexer.tokenize(order)
    result = parser.parse(tokens)
    return result


