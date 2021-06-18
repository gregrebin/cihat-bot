from __future__ import annotations
from configparser import ConfigParser, SectionProxy


class Injector:

    def __init__(self, config: ConfigParser):
        self.config = config

    def inject(self, module: str, name: str, **arguments):
        entry = self.__getattribute__(module)[name]
        arguments = arguments if arguments else entry["args"]
        instance = entry["type"](self.get_config(name), **arguments)
        for submodule in entry["submodules"]:
            sub_instance = self.inject(submodule["module"], submodule["name"])
            instance.__getattribute__(submodule["add"])(sub_instance)
        instance.injector = self
        instance.init()
        return instance

    def get_config(self, section_name: str) -> SectionProxy:
        return self.config[section_name] if section_name in self.config else {}
