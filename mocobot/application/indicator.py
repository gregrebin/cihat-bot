from dataclasses import dataclass
from dataclasses import dataclass
from inspect import getmembers, isclass
from typing import Dict
import ta.momentum, ta.others, ta.trend, ta.volatility, ta.volume
# import pandas_ta as ta


INDICATORS = {
    "momentum": tuple(indicator[0] for indicator in getmembers(ta.momentum, isclass) if indicator[1].__module__ == "ta.momentum"),
    "trend": tuple(indicator[0] for indicator in getmembers(ta.trend, isclass) if indicator[1].__module__ == "ta.trend"),
    "volatility": tuple(indicator[0] for indicator in getmembers(ta.volatility, isclass) if indicator[1].__module__ == "ta.volatility"),
    "volume": tuple(indicator[0] for indicator in getmembers(ta.volume, isclass) if indicator[1].__module__ == "ta.volume"),
    "others": tuple(indicator[0] for indicator in getmembers(ta.others, isclass) if indicator[1].__module__ == "ta.others"),

}


@dataclass(frozen=True)
class Indicator:

    type: str
    name: str
    settings: Dict[str, int]
    min: int
    max: int

    def __post_init__(self):
        if self.type not in INDICATORS:
            raise IndicatorError(f"Invalid indicator type - {self.type}")
        if self.name not in INDICATORS[self.type]:
            raise IndicatorError(f"Invalid indicator name - {self.name}")
        if not self.min <= self.max:
            raise IndicatorError(f"Min should be less than or equal to max - min={self.min} max={self.max} in {self.name}")
        # for setting in self.settings:
        #     if setting not in self._settings:
        #         raise IndicatorError(f"Invalid indicator setting - {setting} in {self.name}")

    @property
    def _indicator(self):
        return ...

    # @property
    # def _function(self) -> Callable:
    #     return object.__getattribute__(ta, self.name)
    #
    # @property
    # def _data(self) -> Tuple[str]:
    #     return tuple(param.name for param in signature(self._function).parameters.values()
    #                  if param.kind == param.POSITIONAL_OR_KEYWORD and param.default == param.empty)
    #
    # @property
    # def _settings(self) -> Tuple[str]:
    #     return tuple(param.name for param in signature(self._function).parameters.values()
    #                  if param.kind == param.POSITIONAL_OR_KEYWORD and not param.default == param.empty)
    #
    # def __call__(self, **data) -> bool:
    #     for data_entry in self._data:
    #         if data_entry not in data:
    #             raise IndicatorError(f"Missing data entry - {data_entry} in {self.name}")
    #     result = self._function(**data, **self.settings)
    #     print(result)
    #     if isinstance(result, Series):
    #         return self.min < result.iloc[-1] < self.max
    #     elif isinstance(result, DataFrame) and self.line in result.columns:
    #         return self.min < result.loc[:, self.line].iloc[-1] < self.max
    #     else:
    #         return False


class IndicatorError(ValueError):
    pass



