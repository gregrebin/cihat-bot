from mocobot.framework.injector import Injector as ModuleInjector
from mocobot.application.application import Application
from mocobot.application.session import Session
from mocobot.traders.test import TestTrader
from mocobot.connectors.test import TestConnector
from mocobot.uis.test import TestUi


class Injector(ModuleInjector):

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




