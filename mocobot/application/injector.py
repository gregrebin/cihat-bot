from mocobot.framework.injector import Injector as ModuleInjector
from mocobot.application.application import Application
from mocobot.application.session import Session
from mocobot.application.ui import Ui
from mocobot.application.trader import Trader
from mocobot.application.connector import Connector
from mocobot.traders.test import TestTrader
from mocobot.connectors.test import TestConnector
from mocobot.uis.socket import SocketUi


class Injector(ModuleInjector):

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
                "type": SocketUi,
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





