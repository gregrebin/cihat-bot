from mocobot.application.market import Interval, OHLCV
from pandas import DataFrame, Series, Timestamp
from dataclasses import dataclass, field
from typing import Dict, Callable, Tuple
from inspect import signature
import pandas_ta as ta


# List of pandas_ta indicators
INDICATORS = DataFrame().ta.indicators(as_list=True)

# Column names of the result of pandas_ta indicators
LINES = {
    "brba": ("ar", "br"),
    "dm": ("+dm", "-dm"),
    "eri": ("bull", "bear"),
    "kst": ("kst", "signal"),
    "macd": ("macd", "histogram", "signal"),
    "ppo": ("ppo", "histogram", "signal"),
    "pvo": ("pvo", "histogram", "signal"),
    "qqe": ("qqe", "basis", "long", "short"),
    "smi": ("smi", "signal", "oscillator"),
    "squeeze": ("sqz", "on", "off", "no"),
    "squeeze_pro": ("sqz", "wide", "normal", "narrow", "off", "no"),
    "stc": ("stc", "macd", "stoch"),
    "stoch": ("k", "d"),
    "stochrsi": ("k", "d"),
    "td_seq": ("up", "down"),
    "hilo": ("line", "long", "short"),
    "supertrend": ("trend", "direction", "long", "short"),
    "drawdown": ("drawdown", "percent", "log"),
    "tos_stdevall": ("central", "lower", "upper"),  # TODO: check columns
    "adx": ("adx", "dmp", "dmn"),
    "amat": ("long", "short"),
    "aroon": ("up", "down", "oscillator"),
    "cksp": ("long", "short"),
    "psar": ("long", "short", "af", "reversal"),
    "tsignals": ("trends", "trades", "entries", "exits"),
    "ttm_trend": "ttm_trend",
    "vortex": ("vip", "vim"),
    "xsignals": ("trends", "trades", "entries", "exits"),
    "aberration": ("zg", "sg", "xg", "atr"),
    "accbands": ("lower", "mid", "upper"),
    "bbands": ("lower", "mid", "upper", "bandwidth", "percent"),
    "donchian": ("lower", "mid", "upper"),
    "hwc": ("mid", "upper", "lower"),
    "kc": ("lower", "upper", "basis"),
    "rvi": ("lower", "upper", "basis"),
    "thermo": ("thermo", "ma", "long", "short"),
    "aobv": ("obv", "min", "max", "fast", "slow", "long", "short"),
    "kvo": ("kvo", "signal"),
}

# Parameter names of pandas_ta functions and relative columns in market dataframe
DATA_NAMES = {
    "_open": OHLCV.OPEN.value,
    "high": OHLCV.CLOSE.value,
    "low": OHLCV.LOW.value,
    "close": OHLCV.CLOSE.value,
    "volume": OHLCV.VOLUME.value,
}

# Custom indicators, lambda must accept one ore more pandas series named as one of DATA_NAMES,
# other optional parameters, and return a series or a dataframe
CUSTOM = {
    "price": lambda close: close,
    "volume": lambda volume: volume,
    "price_change": lambda close: close.apply(lambda x: x - close.iloc[0]),
    "volume_change": lambda volume: volume.apply(lambda x: x - volume.iloc[0]),
}


# Names of indicators that depends on the start point and expect a cropped Dataframe
START_RELATIVE = {
    "price_change",
    "volume_change",
}


@dataclass(frozen=True)
class Indicator:

    name: str
    min: int
    max: int
    line: str = ""
    settings: Dict[str, int] = field(default_factory=dict)
    interval: Interval = field(default_factory=Interval)

    def __post_init__(self):
        if self.name not in INDICATORS and self.name not in CUSTOM:
            raise IndicatorError(f"Invalid indicator name - {self.name}")
        if not self.min <= self.max:
            raise IndicatorError(f"Min should be less than or equal to max - min={self.min} max={self.max} in {self.name}")
        for setting in self.settings:
            if setting not in self._settings:
                raise IndicatorError(f"Invalid indicator setting - {setting} in {self.name}")

    @property
    def _function(self) -> Callable:
        return object.__getattribute__(ta, self.name) if self.name in INDICATORS else CUSTOM[self.name]

    @property
    def _data(self) -> Tuple[str]:
        return tuple(param.name for param in signature(self._function).parameters.values()
                     if param.kind == param.POSITIONAL_OR_KEYWORD and param.default == param.empty)

    @property
    def _settings(self) -> Tuple[str]:
        return tuple(param.name for param in signature(self._function).parameters.values()
                     if param.kind == param.POSITIONAL_OR_KEYWORD and not param.default == param.empty)

    def check(self, dataframe: DataFrame, start: Timestamp = None) -> bool:
        data = {}
        start = start if start else dataframe.index[0]
        if self.name in START_RELATIVE:
            dataframe = dataframe.loc[start:]
        for data_name in self._data:
            data[data_name] = dataframe[DATA_NAMES[data_name]]
        result = self._function(**data, **self.settings)
        if isinstance(result, Series):
            return self.min <= result.iloc[-1] <= self.max
        elif isinstance(result, DataFrame) and self.name in LINES and self.line in LINES[self.name]:
            return self.min <= result.iloc[-1, LINES[self.name].index(self.line)] <= self.max
        else:
            return False

    def __repr__(self):
        settings = f"({','.join(f'{key}:{value}' for key, value in self.settings.items())})" if self.settings else ""
        value = f"{self.min}/{self.max}" if self.max > self.min else f"{self.min}"
        return f"{self.name}@{self.interval}{settings}{self.line}={value}"


class IndicatorError(ValueError):
    pass



