from __future__ import annotations
from dataclasses import dataclass, field, replace, InitVar
from enum import Enum, auto
from typing import Tuple, Dict, Iterable
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

    def update(self, name: str, symbol: str, trade: Trade, interval: Interval, candle: Candle) -> Market:
        if name in self.exchanges:
            exchanges = tuple((exchange.update(symbol, trade, interval, candle) if exchange == name else exchange)
                              for exchange in self.exchanges)
        else:
            exchange = Exchange.factory(name=name, symbol=symbol, trade=trade, interval=interval, candle=candle)
            exchanges = self.exchanges + (exchange,)
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

    def update(self, symbol: str, trade: Trade, interval: Interval, candle: Candle) -> Exchange:
        if symbol in self.pairs:
            pairs = tuple(pair.update(trade, interval, candle) if pair == symbol else pair for pair in self.pairs)
        else:
            pair = Pair.factory(symbol=symbol, trade=trade, interval=interval, candle=candle)
            pairs = self.pairs + (pair,)
        return replace(self, pairs=pairs)

    @staticmethod
    def factory(name: str, symbol: str, trade: Trade, interval: Interval, candle: Candle):
        pairs = (Pair.factory(symbol=symbol, trade=trade, interval=interval, candle=candle),)
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

    def update(self, trade: Trade, interval: Interval, candle: Candle) -> Pair:
        trades = self.trades + (trade,)
        if interval in self.graphs:
            graphs = tuple(graph.update(candle) if graph == interval else graph for graph in self.graphs)
        else:
            graph = Graph.factory(interval=interval, candle=candle)
            graphs = self.graphs + (graph,)
        return replace(self, trades=trades, graphs=graphs)

    @staticmethod
    def factory(symbol: str, trade: Trade, interval: Interval, candle: Candle):
        graphs = (Graph.factory(interval=interval, candle=candle),)
        return Pair(symbol=symbol, trades=(trade,), graphs=graphs)

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

    def update(self, candle: Candle):
        candles = self.candles + (candle,)
        dataframe = self.dataframe.append(self.candles_to_df((candle,)))
        return replace(self, candles=candles, dataframe=dataframe)

    @staticmethod
    def factory(interval: Interval, candle: Candle):
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
