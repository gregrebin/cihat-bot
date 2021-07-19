from __future__ import annotations
from dataclasses import dataclass, field, replace
from enum import Enum, auto
from typing import Tuple, Callable, TypeVar
from pandas import DataFrame, to_datetime


class TimeFrame(Enum):

    MINUTE = "min"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"


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
        chart = Chart(exchange=exchange, symbol=symbol, interval=interval)
        if chart not in charts:
            chart = chart.add_candle(candle=candle)
            charts += (chart,)
        else:
            charts = update_tuple(charts, chart, lambda c: c.add_candle(candle=candle))
        return replace(self, charts=charts)

    def __getitem__(self, item) -> DataFrame:
        exchange, symbol, interval = item
        for chart in self.charts:
            if chart.exchange == exchange and chart.symbol == symbol and chart.interval == interval:
                return chart.candles
        return DataFrame()


@dataclass(frozen=True)
class Chart:

    exchange: str
    symbol: str
    interval: Interval
    candles: DataFrame = field(default_factory=DataFrame, compare=False)

    def add_candle(self, candle: Candle) -> Chart:
        data = {OHLCV.OPEN.value: candle.open, OHLCV.HIGH.value: candle.high, OHLCV.LOW.value: candle.low,
                OHLCV.CLOSE.value: candle.close, OHLCV.VOLUME.value: candle.volume}
        index = to_datetime([candle.time], unit="s", origin="unix")
        candles = self.candles.append(DataFrame(data=data, index=index))
        return replace(self, candles=candles)


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


def update_tuple(t: Tuple[Item, ...], item: Item, update: Callable[[Item], Item]) -> tuple:
    return tuple(update(element) if element == item else element for element in t)
