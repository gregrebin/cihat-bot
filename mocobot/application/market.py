from __future__ import annotations
from dataclasses import dataclass, field, replace, InitVar
from enum import Enum, auto
from typing import Tuple, Dict, Iterable, Any, Callable, TypeVar
from pandas import DataFrame, DatetimeIndex, to_datetime
from collections import namedtuple
import pandas_ta as ta


class TimeFrame(Enum):

    MINUTE = auto()
    HOUR = auto()
    DAY = auto()
    WEEK = auto()
    MONTH = auto()


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

    def get_indicator(self, exchange: str, symbol: str, interval: Interval, indicator: Indicator) -> float:
        pass

    def __getitem__(self, item) -> DataFrame:
        exchange, symbol, interval = item
        for chart in self.charts:
            if chart.exchange == exchange and chart.symbol == symbol and chart.interval == interval:
                return chart.candles


@dataclass(frozen=True)
class Chart:

    exchange: str
    symbol: str
    interval: Interval
    candles: DataFrame = field(default_factory=DataFrame, compare=False)

    def add_candle(self, candle: Candle) -> Chart:
        data = {"open": candle.open, "high": candle.high, "low": candle.low, "close": candle.close, "volume": candle.volume}
        index = to_datetime([candle.time], unit="s", origin="unix")
        candles = self.candles.append(DataFrame(data=data, index=index))
        return replace(self, candles=candles)

    def get_indicator(self, indicator: Indicator) -> float:
        pass


@dataclass(frozen=True)
class Interval:

    quantity: int = 1
    time_frame: TimeFrame = TimeFrame.MINUTE


@dataclass(frozen=True)
class Candle:

    time: int = 0
    open: float = 0
    close: float = 0
    high: float = 0
    low: float = 0
    volume: float = 0


@dataclass(frozen=True)
class Indicator:
    """ Check https://github.com/twopirllc/pandas-ta for all the possibilities """
    name: str
    params: Tuple[Tuple[str, Any], ...] = field(default_factory=tuple)

    def to_dict(self) -> Dict[str, Any]:
        d = dict(self.params)
        d["kind"] = self.name
        return d


Item = TypeVar("Item")


def update_tuple(t: Tuple[Item, ...], item: Item, update: Callable[[Item], Item]) -> tuple:
    return tuple(update(element) if element == item else element for element in t)


# @dataclass(frozen=True)
# class Exchange:
#
#     name: str = ""
#     pairs: Tuple[Pair, ...] = field(default_factory=tuple)
#
#     def candle(self, symbol: str, interval: Interval, candle: Candle):
#         pairs = self.pairs
#         if symbol not in pairs:
#             pairs += (Pair(),)
#         return replace(self, pairs=pairs)
#
#     @staticmethod
#     def from_candle(name: str, symbol: str, interval: Interval, candle: Candle):
#         pairs = (Pair.from_candle(symbol=symbol, interval=interval, candle=candle),)
#         return Exchange(name=name, pairs=pairs)
#
#     def __eq__(self, other) -> bool:
#         if isinstance(other, str):
#             return other == self.name
#         return super().__eq__(other)
#
#     def __getitem__(self, symbol) -> Pair:
#         if isinstance(symbol, str):
#             for pair in self.pairs:
#                 if pair == symbol:
#                     return pair
#
#
# @dataclass(frozen=True)
# class Pair:
#
#     symbol: str = ""
#     charts: Tuple[Chart, ...] = field(default_factory=tuple)
#
#     def candle(self, interval: Interval, candle: Candle):
#         charts = update_tuple(
#             self.charts, interval, lambda chart: chart.candle(candle),
#             lambda: Chart.from_candle(interval=interval, candle=candle)
#         )
#         return replace(self, charts=charts)
#
#     @staticmethod
#     def from_candle(symbol: str, interval: Interval = None, candle: Candle = None):
#         charts = (Chart.from_candle(interval=interval, candle=candle),)
#         return Pair(symbol=symbol, charts=charts)
#
#     def __eq__(self, other) -> bool:
#         if isinstance(other, str):
#             return other == self.symbol
#         return super().__eq__(other)
#
#     def __getitem__(self, interval) -> Chart:
#         if isinstance(interval, Interval):
#             for pair in self.charts:
#                 if pair == interval:
#                     return pair


# @dataclass(frozen=True)
# class Chart:
#
#     interval: Interval = field(default_factory=Interval)
#     dataframe: DataFrame = field(default_factory=DataFrame)
#
#     def candle(self, candle: Candle):
#         candles = self.candles + (candle,)
#         dataframe = self.dataframe.append(self.candles_to_df((candle,)))
#         dataframe = self._ta(dataframe, self.indicators)
#         dataframe, indicators, pending = Chart._try_pending(dataframe, self.indicators, self.pending)
#         return replace(self, candles=candles, dataframe=dataframe, indicators=indicators, pending=pending)
#
#     def indicator(self, indicator: Indicator) -> Chart:
#         dataframe, indicators, pending = Chart._try_new(self.dataframe, indicator, self.indicators, self.pending)
#         return replace(self, dataframe=dataframe, indicators=indicators, pending=pending)
#
#     @staticmethod
#     def from_candle(interval: Interval, candle: Candle) -> Chart:
#         return Chart(interval=interval, candles=(candle,), dataframe=Chart.candles_to_df((candle,)))
#
#     @staticmethod
#     def candles_to_df(candles: Iterable[Candle]) -> DataFrame:
#         return DataFrame(
#             [[candle.time, candle.open, candle.high, candle.low, candle.close, candle.volume] for candle in candles],
#             columns=["timestamp", "open", "high", "low", "close", "volume"],
#             index=DatetimeIndex([candle.time for candle in candles]))
#
#     @staticmethod
#     def _ta(dataframe: DataFrame, indicators: Tuple[Indicator, ...]) -> DataFrame:
#         if indicators:
#             dataframe.ta.strategy(ta.Strategy(name="custom", ta=[indicator.to_dict() for indicator in indicators]))
#         return dataframe
#
#     @staticmethod
#     def _try_new(dataframe: DataFrame, indicator: Indicator, indicators: Tuple[Indicator, ...], pending: Tuple[Indicator, ...]) -> Tuple[DataFrame, Tuple[Indicator, ...], Tuple[Indicator, ...]]:
#         try:
#             dataframe = Chart._ta(dataframe, (indicator,))
#             indicators = indicators + (indicator,)
#         except IndexError:
#             pending = pending + (indicator,)
#         return dataframe, indicators, pending
#
#     @staticmethod
#     def _try_pending(dataframe: DataFrame, indicators: Tuple[Indicator, ...], pending: Tuple[Indicator, ...]) -> Tuple[DataFrame, Tuple[Indicator, ...], Tuple[Indicator, ...]]:
#         for indicator in pending:
#             try:
#                 dataframe = Chart._ta(dataframe, (indicator,))
#                 indicators += (indicator,)
#                 pending = tuple(i for i in pending if i is not indicator)
#             except IndexError:
#                 continue
#         return dataframe, indicators, pending
#
#     def __eq__(self, other) -> bool:
#         if isinstance(other, Interval):
#             return other == self.interval
#         return super().__eq__(other)
#
#     def __getitem__(self, time) -> Candle:
#         if isinstance(time, float):
#             for candle in self.candles:
#                 if candle.time == time:
#                     return candle
