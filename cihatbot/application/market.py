from __future__ import annotations
from dataclasses import dataclass, field
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

    exchanges: Tuple[Exchange] = field(default_factory=tuple)

    def update(self):
        pass


@dataclass(frozen=True)
class Exchange:

    name: str = ""
    time: float = 0
    pairs: Tuple[Pair] = field(default_factory=tuple)

    def update(self):
        pass


@dataclass(frozen=True)
class Pair:

    quote: str = ""
    base: str = ""
    bid: float = 0
    ask: float = 0
    price: float = 0
    candles: Dict[Interval, Tuple[Candle]] = field(default_factory=dict)

    def update(self):
        pass


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

