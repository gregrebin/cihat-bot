from __future__ import annotations
from configparser import ConfigParser, SectionProxy
from typing import Type


class Injector:
    modules = {}

    """
    Example:

    modules = {
        
        Application: {
            "test_app": {
                "type": Application,
                "args": {},
                "submodules": [
                    {"category": Session,
                     "name": "test_session"}
                ]
            }
        },
        
        Session: {
            "test_session": {
                "type": Session,
                "args": {},
                "submodules": [
                    {"category": Trader,
                     "name": "test_trader"},
                    {"category": Ui,
                     "name": "test_ui"}
                ]
            }
        },
        
        Ui: {
            "test_ui": {
                "type": TestUi,
                "args": {},
                "submodules": []
            }
        },
        
        Trader: {
            "test_trader": {
                "type": TestTrader,
                "args": {},
                "submodules": [
                    {"category": Connector,
                     "name": "test_connector"}
                ]
            }
        },
        
        Connector: {
            "test_connector": {
                "type": TestConnector,
                "args": {"username": "username", "password": "password"},
                "submodules": []
            }
        }
    }
    """

    def __init__(self, config: ConfigParser):
        self.config = config

    def inject(self, category: Type, name: str, **arguments):

        if not isinstance(self.modules, dict) or category not in self.modules or name not in self.modules[category]:
            raise InjectorException(f"No {name} in {category.__name__} category")

        entry = self.modules[category][name]

        if not isinstance(entry, dict) or "args" not in entry or "type" not in entry or "submodules" not in entry:
            raise InjectorException(f"Malformed entry for {name} in {category.__name__}")

        arguments = arguments if arguments else entry["args"]
        arguments = {key: value for key, value in arguments.items() if value}

        try:
            instance = entry["type"](self.get_config(name), category, name, **arguments)
        except Exception as exception:
            raise InjectorException(f"Failed initialization of {name} in {category.__name__} ({exception})")

        for submodule in entry["submodules"]:
            if not isinstance(submodule, dict) or "category" not in submodule or "name" not in submodule:
                raise InjectorException(f"Malformed entry for {name} in {category.__name__}")

            sub_instance = self.inject(submodule["category"], submodule["name"])
            instance.add_submodule(sub_instance)

        instance.injector = self
        instance.init()
        return instance

    def get_config(self, section_name: str) -> SectionProxy:
        return self.config[section_name] if section_name in self.config else {}


class InjectorException(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
