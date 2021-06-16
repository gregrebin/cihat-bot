from __future__ import annotations
from dataclasses import dataclass, field, replace, InitVar
from enum import Enum, auto
from typing import Tuple, Dict, Iterable, Any, Callable, TypeVar
from pandas import DataFrame, DatetimeIndex
import pandas_ta as ta


class TimeFrame(Enum):

    MINUTE = auto()
    HOUR = auto()
    DAY = auto()
    WEEK = auto()
    MONTH = auto()


@dataclass(frozen=True)
class Market:

    exchanges: Tuple[Exchange, ...] = field(default_factory=tuple)

    def trade(self, name: str, symbol: str, trade: Trade):
        exchanges = update_tuple(
            self.exchanges, name, lambda exchange: exchange.trade(symbol, trade),
            lambda: Exchange.from_trade(name=name, symbol=symbol, trade=trade)
        )
        return replace(self, exchanges=exchanges)

    def candle(self, name: str, symbol: str, interval: Interval, candle: Candle):
        exchanges = update_tuple(
            self.exchanges, name, lambda exchange: exchange.candle(symbol, interval, candle),
            lambda: Exchange.from_candle(name=name, symbol=symbol, interval=interval, candle=candle)
        )
        return replace(self, exchanges=exchanges)

    def __getitem__(self, name) -> Exchange:
        if isinstance(name, str):
            for exchange in self.exchanges:
                if exchange == name:
                    return exchange


@dataclass(frozen=True)
class Exchange:

    name: str = ""
    time: float = 0
    pairs: Tuple[Pair, ...] = field(default_factory=tuple)

    def trade(self, symbol: str, trade: Trade):
        pairs = update_tuple(
            self.pairs, symbol, lambda pair: pair.trade(trade), lambda: Pair.from_trade(symbol=symbol, trade=trade)
        )
        return replace(self, pairs=pairs)

    def candle(self, symbol: str, interval: Interval, candle: Candle):
        pairs = update_tuple(
            self.pairs, symbol, lambda pair: pair.candle(interval, candle),
            lambda: Pair.from_candle(symbol=symbol, interval=interval, candle=candle)
        )
        return replace(self, pairs=pairs)

    @staticmethod
    def from_trade(name: str, symbol: str, trade: Trade):
        pairs = (Pair.from_trade(symbol=symbol, trade=trade),)
        return Exchange(name=name, pairs=pairs)

    @staticmethod
    def from_candle(name: str, symbol: str, interval: Interval = None, candle: Candle = None):
        pairs = (Pair.from_candle(symbol=symbol, interval=interval, candle=candle),)
        return Exchange(name=name, pairs=pairs)

    def __eq__(self, other) -> bool:
        if isinstance(other, str):
            return other == self.name
        return super().__eq__(other)

    def __getitem__(self, symbol) -> Pair:
        if isinstance(symbol, str):
            for pair in self.pairs:
                if pair == symbol:
                    return pair


@dataclass(frozen=True)
class Pair:

    symbol: str = ""
    trades: Tuple[Trade, ...] = field(default_factory=tuple)
    graphs: Tuple[Graph, ...] = field(default_factory=tuple)

    def trade(self, trade: Trade):
        trades = self.trades + (trade,)
        return replace(self, trades=trades)

    def candle(self, interval: Interval, candle: Candle):
        graphs = update_tuple(
            self.graphs, interval, lambda graph: graph.candle(candle),
            lambda: Graph.from_candle(interval=interval, candle=candle)
        )
        return replace(self, graphs=graphs)

    @staticmethod
    def from_trade(symbol: str, trade: Trade):
        return Pair(symbol=symbol, trades=(trade,))

    @staticmethod
    def from_candle(symbol: str, interval: Interval = None, candle: Candle = None):
        graphs = (Graph.from_candle(interval=interval, candle=candle),)
        return Pair(symbol=symbol, graphs=graphs)

    def __eq__(self, other) -> bool:
        if isinstance(other, str):
            return other == self.symbol
        return super().__eq__(other)

    def __getitem__(self, interval) -> Graph:
        if isinstance(interval, Interval):
            for pair in self.graphs:
                if pair == interval:
                    return pair


@dataclass(frozen=True)
class Trade:

    price: float = 0
    quantity: float = 0


@dataclass(frozen=True)
class Interval:

    quantity: int = 1
    time_frame: TimeFrame = TimeFrame.MINUTE


@dataclass(frozen=True)
class Candle:

    time: float = 0
    open: float = 0
    close: float = 0
    high: float = 0
    low: float = 0
    volume: float = 0


@dataclass(frozen=True)
class Graph:

    interval: Interval = field(default_factory=Interval)
    candles: Tuple[Candle, ...] = field(default_factory=tuple)
    dataframe: DataFrame = field(default_factory=DataFrame)

    def candle(self, candle: Candle):
        candles = self.candles + (candle,)
        dataframe = self.dataframe.append(self.candles_to_df((candle,)))
        return replace(self, candles=candles, dataframe=dataframe)

    @staticmethod
    def from_candle(interval: Interval, candle: Candle):
        return Graph(interval=interval, candles=(candle,), dataframe=Graph.candles_to_df((candle,)))

    @staticmethod
    def candles_to_df(candles: Iterable[Candle]):
        return DataFrame(
            [[candle.time, candle.open, candle.high, candle.low, candle.close, candle.volume] for candle in candles],
            columns=["timestamp", "open", "high", "low", "close", "volume"],
            index=DatetimeIndex([candle.time for candle in candles]))

    def __eq__(self, other) -> bool:
        if isinstance(other, Interval):
            return other == self.interval
        return super().__eq__(other)

    def __getitem__(self, time) -> Candle:
        if isinstance(time, float):
            for candle in self.candles:
                if candle.time == time:
                    return candle


E = TypeVar("E")


def update_tuple(t: Tuple[E, ...], key: Any, update: Callable[[E], E], factory: Callable[[], E]) -> tuple:
    if key in t:
        t = tuple(update(element) if element == key else element for element in t)
    else:
        t += (factory(),)
    return t
