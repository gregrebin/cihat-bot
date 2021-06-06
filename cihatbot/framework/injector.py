from __future__ import annotations
from configparser import ConfigParser
from typing import Type, TypeVar, Callable


ModuleType = TypeVar("ModuleType")


def init(method: Callable) -> Callable:
    def wrapped(self, module_type, name, **arguments) -> ModuleType:
        module = method(self, module_type, name, **arguments)
        module.injector = self
        module.init()
        return module
    return wrapped


class Injector:

    def __init__(self, config: ConfigParser):
        self.config = config

    @init
    def inject(self, module_type: Type[ModuleType], name: str, **arguments: str) -> ModuleType:
        """ Returns the result of the method "name", keyword arguments can be passed to the method. """
        return self.__getattribute__(name)(**arguments)
