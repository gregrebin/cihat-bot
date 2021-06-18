from __future__ import annotations
from configparser import ConfigParser, SectionProxy


class Injector:

    """
    Example:

    app = {
        "test_app": {
            "type": Application,
            "args": {},
            "submodules": [
                {"module": "session",
                 "name": "test_session",
                 "add": "add_session"}
            ]
        }
    }

    session = {
        "test_session": {
            "type": Session,
            "args": {},
            "submodules": [
                {"module": "trader",
                 "name": "test_trader",
                 "add": "add_trader"},
                {"module": "ui",
                 "name": "test_ui",
                 "add": "add_ui"}
            ]
        }
    }

    trader = {
        "test_trader": {
            "type": TestTrader,
            "args": {},
            "submodules": [
                {"module": "connector",
                 "name": "test_connector",
                 "add": "add_connector"}
            ]
        }
    }

    connector = {
        "test_connector": {
            "type": TestConnector,
            "args": {"username": "username", "password": "password"},
            "submodules": []
        }
    }

    ui = {
        "test_ui": {
            "type": TestUi,
            "args": {},
            "submodules": []
        }
    }

    """

    def __init__(self, config: ConfigParser):
        self.config = config

    def inject(self, module: str, name: str, **arguments):
        entry = self.__getattribute__(module)[name]
        arguments = arguments if arguments else entry["args"]
        instance = entry["type"](self.get_config(name), name, **arguments)
        for submodule in entry["submodules"]:
            sub_instance = self.inject(submodule["module"], submodule["name"])
            instance.__getattribute__(submodule["add"])(sub_instance)
        instance.injector = self
        instance.init()
        return instance

    def get_config(self, section_name: str) -> SectionProxy:
        return self.config[section_name] if section_name in self.config else {}
