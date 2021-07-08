from pandas import DataFrame, Series
from dataclasses import dataclass, field
from typing import Union, Dict
import pandas_ta as ta


INDICATORS = DataFrame().ta.indicators(as_list=True)


@dataclass(frozen=True)
class Indicator:

    name: str
    args: Dict[str, int]
    min: int
    max: int

    def __post_init__(self):
        if self.name not in INDICATORS:
            raise IndicatorError(f"Invalid indicator name - {self.name}")
        if not self.min <= self.max:
            raise IndicatorError(f"Min should be less than or equal to max - min={self.min} max={self.max} in {self.name}")
        func = object.__getattribute__(ta, self.name)
        var_names = func.__code__.co_varnames
        print(var_names)
        for arg in self.args:
            if arg not in var_names:
                raise IndicatorError(f"Invalid indicator argument - {arg} in {self.name}")

    def __call__(self, *args) -> Union[Series, DataFrame]:
        func = object.__getattribute__(ta, self.name)
        return func(*args, **self.args)


class IndicatorError(ValueError):
    pass



