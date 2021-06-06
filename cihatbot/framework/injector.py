from __future__ import annotations
from configparser import ConfigParser
from typing import Type, TypeVar, Callable


ModuleType = TypeVar("ModuleType")


def init(method: Callable) -> Callable:
    def wrapped(self, module_type, name) -> ModuleType:
        module = method(self, module_type, name)
        module.injector = self
        module.init()
        return module
    return wrapped


class Injector:

    def __init__(self, config: ConfigParser):
        self.config = config

    @init
    def inject(self, t: Type[ModuleType], name: str) -> ModuleType:
        return self.__getattribute__(name)()
