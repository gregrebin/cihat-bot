from mocobot.framework.injector import Injector as FrameworkInjector
from mocobot.application.application import Application
from mocobot.application.ui import Ui
from mocobot.application.trader import Trader
from mocobot.application.connector import Connector
from mocobot.connectors.test import TestConnector
from mocobot.connectors.binance import BinanceConnector
from mocobot.uis.socket import SocketUi
from mocobot.uis.test import TestUi


class Injector(FrameworkInjector):

    modules = {

        Application: {
            "default_app": {
                "type": Application,
                "args": {},
                "submodules": [
                    {"category": Trader, "name": "default_trader"}
                ]
            },
            "test_app": {
                "type": Application,
                "args": {},
                "submodules": [
                    {"category": Trader, "name": "test_trader"}
                ]
            }
        },

        Trader: {
            "default_trader": {
                "type": Trader,
                "args": {},
                "submodules": [
                    {"category": Ui, "name": "socket_ui"}
                ]
            },
            "test_trader": {
                "type": Trader,
                "args": {},
                "submodules": [
                    {"category": Connector, "name": "test_connector"},
                    {"category": Ui, "name": "test_ui"}
                ]
            }
        },

        Ui: {
            "socket_ui": {
                "type": SocketUi,
                "args": {},
                "submodules": []
            },
            "test_ui": {
                "type": TestUi,
                "args": {},
                "submodules": []
            }
        },

        Connector: {
            "binance_connector": {
                "type": BinanceConnector,
                "args": {},
                "submodules": []
            },
            "test_connector": {
                "type": TestConnector,
                "args": {"username": "username", "password": "password"},
                "submodules": []
            },
            "test_connector_no_args": {
                "type": TestConnector,
                "args": {},
                "submodules": []
            }
        }
    }





