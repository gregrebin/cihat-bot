from __future__ import annotations
from dataclasses import dataclass, field, replace
from enum import Enum, auto
from typing import Tuple, Dict
from pandas import DataFrame


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
            pairs = (Pair(symbol=symbol, trades=(trade,), candles={interval: (candle,)},
                          candles_df={interval: candle_to_df(candle)}),)
            exchanges = self.exchanges + (Exchange(name=name, pairs=pairs),)
        return replace(self, exchanges=exchanges)


@dataclass(frozen=True)
class Exchange:

    name: str = ""
    time: float = 0
    pairs: Tuple[Pair, ...] = field(default_factory=tuple)

    def update(self, symbol: str, trade: Trade, interval: Interval, candle: Candle) -> Exchange:
        if symbol in self.pairs:
            pairs = tuple(pair.update(trade, interval, candle) if pair == symbol else pair for pair in self.pairs)
        else:
            pairs = self.pairs + (Pair(symbol=symbol, trades=(trade,), candles={interval: (candle,)},
                                       candles_df={interval: candle_to_df(candle)}),)
        return replace(self, pairs=pairs)

    def __eq__(self, other) -> bool:
        if isinstance(other, str):
            return other == self.name
        else:
            return super().__eq__(other)


@dataclass(frozen=True)
class Pair:

    symbol: str = ""
    trades: Tuple[Trade, ...] = field(default_factory=tuple)
    candles: Dict[Interval, Tuple[Candle, ...]] = field(default_factory=dict)
    candles_df: Dict[Interval, DataFrame] = field(default_factory=dict)

    def update(self, trade: Trade, interval: Interval, candle: Candle) -> Pair:
        trades = self.trades + (trade,)
        candles = self.candles
        candles_df = self.candles_df
        new_df = candle_to_df(candle)
        if interval in candles:
            candles[interval] += (candle,)
            candles_df[interval] = candles_df[interval].append(new_df)
        else:
            candles[interval] = (candle,)
            candles_df[interval] = new_df
        return replace(self, trades=trades, candles=candles, candles_df=candles_df)

    def __eq__(self, other) -> bool:
        if isinstance(other, str):
            return other == self.symbol
        else:
            return super().__eq__(other)


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


def candle_to_df(candle: Candle) -> DataFrame:
    return DataFrame({"Timestamp": [candle.time], "Open": [candle.open], "High": [candle.high], "Low": [candle.low],
                      "Close": [candle.close], "Volume": [candle.volume]})
