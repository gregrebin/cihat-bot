from mocobot.framework.injector import Injector as ModuleInjector
from mocobot.application.application import Application
from mocobot.application.session import Session
from mocobot.application.ui import Ui
from mocobot.application.trader import Trader
from mocobot.application.connector import Connector
from mocobot.traders.real import RealTrader
from mocobot.traders.test import TestTrader
from mocobot.connectors.test import TestConnector
from mocobot.connectors.binance import BinanceConnector
from mocobot.uis.socket import SocketUi
from mocobot.uis.test import TestUi


class Injector(ModuleInjector):

    modules = {

        Application: {
            "default_app": {
                "type": Application,
                "args": {},
                "submodules": [
                    {"category": Session,
                     "name": "default_session"}
                ]
            },
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
            "default_session": {
                "type": Session,
                "args": {},
                "submodules": [
                    {"category": Trader,
                     "name": "real_trader"},
                    {"category": Ui,
                     "name": "socket_ui"}
                ]
            },
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

        Trader: {
            "real_trader": {
                "type": RealTrader,
                "args": {},
                "submodules": []
            },
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
            "binance_connector": {
                "type": BinanceConnector,
                "args": {},
                "submodules": []
            },
            "test_connector": {
                "type": TestConnector,
                "args": {"username": "username", "password": "password"},
                "submodules": []
            }
        }
    }





