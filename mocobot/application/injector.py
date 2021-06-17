from mocobot.framework.injector import Injector as ModuleInjector, Type, ModuleType
from mocobot.application.application import Application
from mocobot.application.session import Session
from mocobot.application.trader import Trader
from mocobot.traders.test import TestTrader
from mocobot.application.connector import Connector
from mocobot.connectors.test import TestConnector
from mocobot.connectors.binance import BinanceConnector
from mocobot.application.ui import Ui
from mocobot.uis.test import TestUi
from configparser import SectionProxy


class Injector(ModuleInjector):

    def test_app(self):
        app = Application(self.get_config("app"))
        app.add_session(self.inject(Session, "test_session"))
        return app

    def test_session(self):
        session = Session(self.get_config("session"))
        session.add_trader(self.inject(Trader, "test_trader"))
        session.add_ui(self.inject(Ui, "test_ui"))
        return session

    def test_trader(self):
        trader = TestTrader(self.get_config("trader"))
        trader.add_connector(self.inject(Connector, "test_connector", username="username", password="password"))
        return trader

    def test_connector(self, username, password):
        connector = TestConnector(self.get_config("connector"), username, password)
        return connector

    def binance_connector(self, username, password):
        connector = BinanceConnector(self.get_config("connector"), username, password)
        return connector

    def test_ui(self):
        ui = TestUi(self.get_config("test"))
        return ui

    def get_config(self, section_name: str) -> SectionProxy:
        return self.config[section_name] if section_name in self.config else {}

    # Needed for type hinting
    def inject(self, module_type: Type[ModuleType], name: str, **arguments) -> ModuleType:
        return super().inject(module_type, name, **arguments)



