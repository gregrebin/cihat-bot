from cihatbot.framework.injector import Injector as ModuleInjector, Type, ModuleType
from cihatbot.application.application import Application
from cihatbot.application.session import Session
from cihatbot.application.trader import Trader
from cihatbot.traders.test import TestTrader
from cihatbot.application.connector import Connector
from cihatbot.connectors.test import TestConnector
from cihatbot.application.ui import Ui
from cihatbot.uis.test import TestUi


class Injector(ModuleInjector):

    def test_app(self):
        app = Application(self.config["app"])
        app.add_session(self.inject(Session, "test_session"))
        return app

    def test_session(self):
        session = Session({})
        session.add_trader(self.inject(Trader, "test_trader"))
        session.add_ui(self.inject(Ui, "test_ui"))
        return session

    def test_trader(self):
        trader = TestTrader({})
        trader.add_connector(self.inject(Connector, "test_connector"))
        return trader

    def test_connector(self):
        connector = TestConnector({}, "user", "password")
        return connector

    def test_ui(self):
        ui = TestUi({})
        return ui

    # Needed for type hinting
    def inject(self, module_type: Type[ModuleType], name: str, **arguments) -> ModuleType:
        return super().inject(module_type, name, **arguments)



