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

    def indicator(self, name: str, symbol: str, interval: Interval, indicator: Indicator):
        """ Should be added to an existent chart, otherwise will be ignored """
        exchanges = update_tuple(
            self.exchanges, name, lambda exchange: exchange.indicator(symbol, interval, indicator),
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

    def indicator(self, symbol: str, interval: Interval, indicator: Indicator):
        pairs = update_tuple(
            self.pairs, symbol, lambda pair: pair.indicator(interval, indicator)
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
    charts: Tuple[Chart, ...] = field(default_factory=tuple)

    def trade(self, trade: Trade):
        trades = self.trades + (trade,)
        return replace(self, trades=trades)

    def candle(self, interval: Interval, candle: Candle):
        charts = update_tuple(
            self.charts, interval, lambda chart: chart.candle(candle),
            lambda: Chart.from_candle(interval=interval, candle=candle)
        )
        return replace(self, charts=charts)

    def indicator(self, interval: Interval, indicator: Indicator):
        charts = update_tuple(
            self.charts, interval, lambda chart: chart.indicator(indicator)
        )
        return replace(self, charts=charts)

    @staticmethod
    def from_trade(symbol: str, trade: Trade):
        return Pair(symbol=symbol, trades=(trade,))

    @staticmethod
    def from_candle(symbol: str, interval: Interval = None, candle: Candle = None):
        charts = (Chart.from_candle(interval=interval, candle=candle),)
        return Pair(symbol=symbol, charts=charts)

    def __eq__(self, other) -> bool:
        if isinstance(other, str):
            return other == self.symbol
        return super().__eq__(other)

    def __getitem__(self, interval) -> Chart:
        if isinstance(interval, Interval):
            for pair in self.charts:
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
class Chart:

    interval: Interval = field(default_factory=Interval)
    candles: Tuple[Candle, ...] = field(default_factory=tuple)
    dataframe: DataFrame = field(default_factory=DataFrame)
    indicators: Tuple[Indicator, ...] = field(default_factory=tuple)
    pending: Tuple[Indicator, ...] = field(default_factory=tuple)

    def candle(self, candle: Candle):
        candles = self.candles + (candle,)
        dataframe = self.dataframe.append(self.candles_to_df((candle,)))
        dataframe = self._ta(dataframe, self.indicators)
        dataframe, indicators, pending = Chart._try_pending(dataframe, self.indicators, self.pending)
        return replace(self, candles=candles, dataframe=dataframe, indicators=indicators, pending=pending)

    def indicator(self, indicator: Indicator) -> Chart:
        dataframe, indicators, pending = Chart._try_new(self.dataframe, indicator, self.indicators, self.pending)
        return replace(self, dataframe=dataframe, indicators=indicators, pending=pending)

    @staticmethod
    def from_candle(interval: Interval, candle: Candle) -> Chart:
        return Chart(interval=interval, candles=(candle,), dataframe=Chart.candles_to_df((candle,)))

    @staticmethod
    def candles_to_df(candles: Iterable[Candle]) -> DataFrame:
        return DataFrame(
            [[candle.time, candle.open, candle.high, candle.low, candle.close, candle.volume] for candle in candles],
            columns=["timestamp", "open", "high", "low", "close", "volume"],
            index=DatetimeIndex([candle.time for candle in candles]))

    @staticmethod
    def _ta(dataframe: DataFrame, indicators: Tuple[Indicator, ...]) -> DataFrame:
        if indicators:
            dataframe.ta.strategy(ta.Strategy(name="custom", ta=[indicator.to_dict() for indicator in indicators]))
        return dataframe

    @staticmethod
    def _try_new(dataframe: DataFrame, indicator: Indicator, indicators: Tuple[Indicator, ...], pending: Tuple[Indicator, ...]) -> Tuple[DataFrame, Tuple[Indicator, ...], Tuple[Indicator, ...]]:
        try:
            dataframe = Chart._ta(dataframe, (indicator,))
            indicators = indicators + (indicator,)
        except IndexError:
            pending = pending + (indicator,)
        return dataframe, indicators, pending

    @staticmethod
    def _try_pending(dataframe: DataFrame, indicators: Tuple[Indicator, ...], pending: Tuple[Indicator, ...]) -> Tuple[DataFrame, Tuple[Indicator, ...], Tuple[Indicator, ...]]:
        for indicator in pending:
            try:
                dataframe = Chart._ta(dataframe, (indicator,))
                indicators += (indicator,)
                pending = tuple(i for i in pending if i is not indicator)
            except IndexError:
                continue
        return dataframe, indicators, pending

    def __eq__(self, other) -> bool:
        if isinstance(other, Interval):
            return other == self.interval
        return super().__eq__(other)

    def __getitem__(self, time) -> Candle:
        if isinstance(time, float):
            for candle in self.candles:
                if candle.time == time:
                    return candle


@dataclass(frozen=True)
class Indicator:
    """ Check https://github.com/twopirllc/pandas-ta for all the possibilities """
    name: str
    params: Tuple[Tuple[str, Any], ...] = field(default_factory=tuple)

    def to_dict(self) -> Dict[str, Any]:
        d = dict(self.params)
        d["kind"] = self.name
        return d


E = TypeVar("E")


def update_tuple(t: Tuple[E, ...], key: Any, update: Callable[[E], E] = None, factory: Callable[[], E] = None) -> tuple:
    present = key in t
    if update and present:
        t = tuple(update(element) if element == key else element for element in t)
    elif factory and not present:
        t += (factory(),)
    return t
