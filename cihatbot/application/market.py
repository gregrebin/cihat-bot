from __future__ import annotations
from dataclasses import dataclass, field, replace
from enum import Enum, auto
from typing import Tuple, Dict


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
            pairs = (Pair(symbol=symbol, trades=(trade,), candles={interval: (candle,)}),)
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
            pairs = self.pairs + (Pair(symbol=symbol),)
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

    def update(self, trade: Trade, interval: Interval, candle: Candle) -> Pair:
        trades = self.trades + (trade,)
        candles = self.candles
        if interval in candles:
            candles[interval] += (candle,)
        else:
            candles[interval] = (candle,)
        return replace(self, trades=trades, candles=candles)

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

    open: float = 0
    close: float = 0
    height: float = 0
    low: float = 0
    volume: float = 0
