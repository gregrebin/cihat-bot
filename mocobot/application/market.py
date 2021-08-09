from __future__ import annotations
from dataclasses import dataclass, field, replace
from enum import Enum, auto
from typing import Tuple, Callable, TypeVar, Any
from pandas import DataFrame, Timestamp, to_datetime


class TimeFrame(Enum):

    MINUTE = "m"
    HOUR = "h"
    DAY = "d"
    WEEK = "w"
    MONTH = "M"


class OHLCV(Enum):

    OPEN = "open"
    HIGH = "high"
    LOW = "low"
    CLOSE = "close"
    VOLUME = "volume"


@dataclass(frozen=True)
class Market:

    charts: Tuple[Chart, ...] = field(default_factory=tuple)

    def add_candle(self, exchange: str, symbol: str, interval: Interval, candle: Candle) -> Market:
        charts = self.charts
        info = ChartInfo(exchange=exchange, symbol=symbol, interval=interval)
        if info not in charts:
            chart = Chart(info=info)
            chart = chart.add_candle(candle=candle)
            charts += (chart,)
        else:
            charts = update_tuple(charts, info, lambda c: c.add_candle(candle=candle))
        return replace(self, charts=charts)

    def __getitem__(self, info: ChartInfo) -> DataFrame:
        for chart in self.charts:
            if chart == info:
                return chart.candles
        return DataFrame()


@dataclass(frozen=True)
class Chart:

    info: ChartInfo
    candles: DataFrame = field(default_factory=DataFrame, compare=False)

    def add_candle(self, candle: Candle) -> Chart:
        data = {OHLCV.OPEN.value: candle.open, OHLCV.HIGH.value: candle.high, OHLCV.LOW.value: candle.low,
                OHLCV.CLOSE.value: candle.close, OHLCV.VOLUME.value: candle.volume}
        index = Timestamp(candle.time, unit="s")
        if index in self.candles.index:
            candles = self.candles.copy()
            candles.loc[index] = data
        else:
            candles = self.candles.append(DataFrame(data=data, index=[index]))
            candles.sort_index(inplace=True)
        return replace(self, candles=candles)

    def __eq__(self, other):
        if isinstance(other, ChartInfo):
            return self.info == other
        else:
            return super().__eq__(other)


@dataclass(frozen=True)
class ChartInfo:

    exchange: str
    symbol: str
    interval: Interval


@dataclass(frozen=True)
class Interval:

    quantity: int = 1
    time_frame: TimeFrame = TimeFrame.MINUTE

    def __repr__(self):
        return f"{self.quantity}{self.time_frame.value}"


@dataclass(frozen=True)
class Candle:

    time: int = 0
    open: float = 0
    close: float = 0
    high: float = 0
    low: float = 0
    volume: float = 0


Item = TypeVar("Item")


def update_tuple(t: Tuple[Item, ...], item: Any, update: Callable[[Item], Item]) -> tuple:
    return tuple(update(element) if element == item else element for element in t)
