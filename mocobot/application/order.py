from __future__ import annotations
from mocobot.application.indicator import Indicator, Interval
from mocobot.application.market import TimeFrame, ChartInfo
from typing import List, Callable, Dict, Tuple, Generator, Set
from uuid import uuid4, UUID
from enum import Enum, auto
from dataclasses import dataclass, field, replace
from abc import ABC, abstractmethod
from sly import Lexer, Parser
from time import time, gmtime


def new_uid():
    return uuid4().hex


def current_time():
    return int(time())


class Status(Enum):
    NEW = "new"
    SUBMITTED = "submitted"
    CANCELLED = "cancelled"
    FILLED = "filled"
    REJECTED = "rejected"


class Command(Enum):
    BUY = "buy"
    SELL = "sell"


class Mode(Enum):
    PARALLEL = "parallel"
    SEQUENT = "sequent"


@dataclass(frozen=True, repr=False)
class Order(ABC):

    @staticmethod
    def parse(order: str):
        return OrderParser().parse(OrderLexer().tokenize(order))

    @abstractmethod
    def add(self, order: Order, mode: Mode) -> Order:
        pass

    @abstractmethod
    def cancel(self, uid: str) -> Order:
        pass

    @abstractmethod
    def requirements(self) -> Generator[Requirement, None, None]:
        pass

    @abstractmethod
    def get(self) -> Generator[Single, None, None]:
        pass

    @abstractmethod
    def set_eid(self, uid: str, eid: str) -> Order:
        pass

    @abstractmethod
    def update_status(self, uid: str = None, eid: str = None, status: Status = None) -> Order:
        pass

    def _add(self, order: Order, mode: Mode) -> Order:
        orders = self._add_term(mode) + order._add_term(mode)
        return Multiple(mode=mode, orders=orders)

    def _add_term(self, mode: Mode) -> Tuple[Order, ...]:
        return self,

    def __repr__(self):
        return self._repr_()

    @abstractmethod
    def _repr_(self, depth=0):
        pass


@dataclass(frozen=True, repr=False)
class Empty(Order):

    value: str = field(init=False, default="empty")

    def add(self, order: Order, mode: Mode) -> Order:
        return order

    def cancel(self, uid: str) -> Order:
        return self

    def requirements(self) -> Generator[Requirement, None, None]:
        return
        yield

    def get(self) -> Generator[Single, None, None]:
        return
        yield

    def set_eid(self, uid: str, eid: str) -> Order:
        return self

    def update_status(self, uid: str = None, eid: str = None, status: Status = None) -> Order:
        return self

    def _repr_(self, depth=0):
        return Empty.value


@dataclass(frozen=True, repr=False)
class Single(Order):

    status: Status = Status.NEW
    to_cancel: bool = False
    uid: str = field(default_factory=new_uid)
    eid: str = ""

    command: Command = Command.BUY
    exchange: str = ""
    symbol: str = ""
    quote: float = 0
    base: float = 0
    price: float = 0

    time: int = field(default_factory=current_time)
    indicators: Tuple[Indicator, ...] = field(default_factory=tuple)

    def __post_init__(self):
        if not self.price:
            return
        if self.quote <= 0:
            object.__setattr__(self, "quote", self.base / self.price)
        else:
            object.__setattr__(self, "base", self.quote * self.price)

    def add(self, order: Order, mode: Mode) -> Order:
        return super()._add(order, mode)

    def cancel(self, uid: str) -> Order:
        if self.uid == uid and self.status is Status.NEW:
            order = replace(self, status=Status.CANCELLED)
            return order
        elif self.uid == uid and self.status is Status.SUBMITTED:
            return replace(self, to_cancel=True)
        return self

    def requirements(self) -> Generator[Requirement, None, None]:
        for indicator in self.indicators:
            yield Requirement(
                time=self.time,
                info=ChartInfo(exchange=self.exchange, symbol=self.symbol, interval=indicator.interval)
            )

    def get(self) -> Generator[Single, None, None]:
        if self.status not in (Status.NEW, Status.SUBMITTED):
            return
        yield self

    def set_eid(self, uid: str, eid: str) -> Order:
        if self.uid == uid:
            return replace(self, eid=eid)
        else:
            return self

    def update_status(self, uid: str = None, eid: str = None, status: Status = None) -> Order:
        if (uid and self.uid == uid) or (eid and self.eid == eid):
            status = status if status else self.status
            return replace(self, status=status)
        else:
            return self

    def _repr_(self, depth=0):
        tm = gmtime(self.time)

        return f"{self.command.value} {self.quote} {self.symbol} in {self.exchange} at {self.price} for {self.base}" \
               f" on {tm.tm_mday}.{tm.tm_mon}.{tm.tm_year} {tm.tm_hour}:{tm.tm_min}" \
               f"{' if ' + ' and '.join(indicator.__repr__() for indicator in self.indicators) if self.indicators else ''}" \
               f" <{self.status.value if not self.to_cancel else 'to_cancel'}-{self.uid}-{self.eid}>"


@dataclass(frozen=True, repr=False)
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

    def cancel(self, uid: str) -> Order:
        orders = tuple(order.cancel(uid) for order in self.orders)
        return replace(self, orders=orders)

    def requirements(self) -> Generator[Requirement, None, None]:
        for order in self.orders:
            for requirement in order.requirements():
                yield requirement

    def get(self) -> Generator[Single, None, None]:
        for order in self.orders:
            empty = True
            for single in order.get():
                empty = False
                yield single
            if self.mode is Mode.SEQUENT and not empty:
                break

    def set_eid(self, uid: str, eid: str) -> Order:
        orders = tuple(order.set_eid(uid=uid, eid=eid) for order in self.orders)
        return replace(self, orders=orders)

    def update_status(self, uid: str = None, eid: str = None, status: Status = None) -> Order:
        orders = tuple(order.update_status(uid=uid, eid=eid, status=status) for order in self.orders)
        return replace(self, orders=orders)

    def _repr_(self, depth=1):
        tab = "\t" * depth
        orders = ",\n".join(tab + order._repr_(depth=depth+1) for order in self.orders)
        return f"[{self.mode.value}\n{orders}]"


@dataclass(frozen=True)
class Requirement:

    time: int
    info: ChartInfo


# Parser formal grammar:
# ---------------
# order ::= <empty> | <single> | <multiple>
#   empty ::= ""
#   single ::= <command> <quote> <symbol> in <exchange> at <price> <conditions> | <command> <symbol> in <exchange> at <price> for <base> <conditions>  (ex. buy 5 BTCUSDT in Binance at 20000 | buy BTCUSDT in Binance at 20000 for 1000 | buy 5 BTCUSDT in Binance at 20000 if price=20000/23000 and macd@1d(fast:8,slow:1)histogram=1)
#       command ::= buy | sell
#       quote ::= <decimal>
#       symbol ::= <string>
#       exchange ::= <string>
#       price ::= <decimal>
#       base ::= <string>
#       conditions ::=  | if <indicators>
#           <indicators> ::= <indicator> | <indicator> and <indicators>
#               <indicator> ::= <name> <interval> = <value> | <name> <interval> ( <settings> ) = <value> | <name> <interval> ( <settings> ) <line> = <value>
#                   <name> ::= <string>
#                   <interval> ::= @ <decimal> <timeframe> | ""
#                   <value> ::= <decimal> | <decimal> / <decimal>
#                   <settings> ::= <setting> | <setting> , <settings>
#                       <setting> ::= <string> : <decimal>
#                   <line> ::= <string>
#   multiple ::= [<mode> <orders>] (ex. [parallel buy 5 BTCUSDT in Binance at 30000; buy ETHUSDT in Coinbase at 2000 for 1000])
#       mode ::= parallel | sequent
#       orders ::= <order> | <order> ; <orders>


# noinspection PyUnresolvedReferences,PyUnboundLocalVariable,PyPep8Naming,PyRedeclaration,PyMethodMayBeStatic
class OrderLexer(Lexer):

    tokens = {EMPTY, COMMAND, MODE, IN, AT, FOR, IF, AND, SEMICOLON, LBRACKET, RBRACKET, LPAR, RPAR, EQUAL, COMMA, COLON, SLASH, INTERVAL, DECIMAL, STRING}

    ignore = " \t\n\r"

    EMPTY = Empty.value
    COMMAND = f"({Command.BUY.value}|{Command.SELL.value})"
    MODE = f"({Mode.PARALLEL.value}|{Mode.SEQUENT.value})"
    IN = "in"
    AT = "at"
    FOR = "for"
    IF = "if"
    AND = "and"
    SEMICOLON = ";"
    LBRACKET = "\["
    RBRACKET = "\]"
    LPAR = "\("
    RPAR = "\)"
    EQUAL = "="
    COMMA = ","
    COLON = ":"
    SLASH = "/"
    INTERVAL = "@\d+[mhdwM]"
    DECIMAL = "\d+\.?\d*"
    STRING = "\w+"

    def COMMAND(self, t):
        t.value = Command(t.value)
        return t

    def MODE(self, t):
        t.value = Mode(t.value)
        return t

    def INTERVAL(self, t):
        t.value = Interval(quantity=int(t.value[1:-1]), time_frame=TimeFrame(t.value[-1]))
        return t

    def DECIMAL(self, t):
        t.value = float(t.value)
        return t


# noinspection PyUnresolvedReferences
class OrderParser(Parser):

    tokens = OrderLexer.tokens

    @_("EMPTY")
    def order(self, p):
        return Empty()

    @_("single")
    def order(self, p):
        return p.single

    @_("multiple")
    def order(self, p):
        return p.multiple

    #  Multiple

    @_("LBRACKET MODE orders RBRACKET")
    def multiple(self, p):
        return Multiple(mode=p.MODE, orders=p.orders)

    @_("order SEMICOLON orders")
    def orders(self, p):
        return (p.order,) + p.orders

    @_("order")
    def orders(self, p):
        return p.order,

    #  Single

    @_("COMMAND quote symbol IN exchange AT price conditions")
    def single(self, p):
        return Single(command=p.COMMAND, quote=p.quote, symbol=p.symbol, exchange=p.exchange, price=p.price, indicators=p.conditions)

    @_("COMMAND symbol IN exchange AT price FOR base conditions")
    def single(self, p):
        return Single(command=p.COMMAND, symbol=p.symbol, exchange=p.exchange, price=p.price, base=p.base, indicators=p.conditions)

    @_("DECIMAL")
    def quote(self, p):
        return p.DECIMAL

    @_("STRING")
    def symbol(self, p):
        return p.STRING

    @_("STRING")
    def exchange(self, p):
        return p.STRING

    @_("DECIMAL")
    def price(self, p):
        return p.DECIMAL

    @_("DECIMAL")
    def base(self, p):
        return p.DECIMAL

    #  Conditions

    @_("")
    def conditions(self, p):
        return ()

    @_("IF indicators")
    def conditions(self, p):
        return p.indicators

    @_("indicator AND indicators")
    def indicators(self, p):
        return (p.indicator,) + p.indicators

    @_("indicator")
    def indicators(self, p):
        return p.indicator,

    @_("name interval EQUAL value")
    def indicator(self, p):
        value = p.value
        return Indicator(name=p.name, interval=p.interval, min=value[0], max=value[1], settings={})

    @_("name interval LPAR settings RPAR EQUAL value")
    def indicator(self, p):
        value = p.value
        settings = dict(p.settings)
        return Indicator(name=p.name, interval=p.interval, min=value[0], max=value[1], settings=settings)

    @_("name interval LPAR settings RPAR line EQUAL value")
    def indicator(self, p):
        value = p.value
        settings = dict(p.settings)
        return Indicator(name=p.name, interval=p.interval, min=value[0], max=value[1], settings=settings, line=p.line)

    @_("STRING")
    def name(self, p):
        return p.STRING

    @_("INTERVAL", "")
    def interval(self, p):
        if len(p) == 1:
            return p.INTERVAL
        else:
            return Interval()

    @_("DECIMAL", "DECIMAL SLASH DECIMAL")
    def value(self, p):
        if len(p) == 1:
            return p.DECIMAL, p.DECIMAL
        else:
            return p.DECIMAL0, p.DECIMAL1

    @_("setting COMMA settings")
    def settings(self, p):
        return (p.setting,) + p.settings

    @_("setting")
    def settings(self, p):
        return p.setting,

    @_("STRING COLON DECIMAL")
    def setting(self, p):
        return p.STRING, p.DECIMAL

    @_("STRING")
    def line(self, p):
        return p.STRING






