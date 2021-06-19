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
        entry = self.modules[category][name]
        arguments = arguments if arguments else entry["args"]
        instance = entry["type"](self.get_config(name), category, name, **arguments)
        for submodule in entry["submodules"]:
            sub_instance = self.inject(submodule["category"], submodule["name"])
            instance.add_submodule(sub_instance)
        instance.injector = self
        instance.init()
        return instance

    def get_config(self, section_name: str) -> SectionProxy:
        return self.config[section_name] if section_name in self.config else {}
