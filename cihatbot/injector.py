from cihatbot.module import Module, Injector as ModuleInjector
from cihatbot.app import Application
from cihatbot.user import User
from cihatbot.ui.ui import Ui
from cihatbot.ui.telegram import Telegram
from cihatbot.parser.parser import Parser
from cihatbot.parser.simple_parser import SimpleParser
from cihatbot.trader.trader import Trader
from cihatbot.trader.real import RealTrader
from cihatbot.connector.connector import Connector
from cihatbot.connector.binance import BinanceConnector
from configparser import ConfigParser
from typing import Callable


def inject_self(function: Callable) -> Callable:
    def wrapped(self, name) -> Module:
        module = function(self, name)
        module.injector = self
        return module
    return wrapped


class Injector(ModuleInjector):

    def __init__(self, config: ConfigParser):
        self.config = config

    @inject_self
    def inject_app(self, name: str) -> Application:
        app = Application(self.config["app"]).init()
        app.add_user(self.inject_user("user"))
        return app

    @inject_self
    def inject_user(self, name: str) -> User:
        user = User(self.config["user"]).init()
        user.add_ui(self.inject_ui("telegram_ui"))
        user.add_trader(self.inject_trader("real_trader"))
        return user

    @inject_self
    def inject_ui(self, name: str) -> Ui:
        parser = self.inject_parser("simple_parser")
        ui = Telegram(self.config["telegram-ui"], parser).init()
        return ui

    @inject_self
    def inject_parser(self, name: str) -> Parser:
        parser = SimpleParser()
        return parser

    @inject_self
    def inject_trader(self, name: str) -> Trader:
        connector = self.inject_connector("binance_connector")
        trader = RealTrader(self.config, connector).init()
        return trader

    @inject_self
    def inject_connector(self, name: str) -> Connector:
        connector = BinanceConnector()
        return connector


