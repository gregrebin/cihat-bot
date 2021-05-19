from cihatbot.framework.module import Module
from cihatbot.framework.injector import Injector as ModuleInjector
from cihatbot.application.application import Application
from cihatbot.application.user import User
from cihatbot.application.ui import Ui
from cihatbot.uis.telegram import Telegram
from cihatbot.application.parser import Parser
from cihatbot.parsers.simple_parser import SimpleParser
from cihatbot.application.trader import Trader
from cihatbot.traders.real import RealTrader
from cihatbot.application.connector import Connector
from cihatbot.connectors.binance import BinanceConnector
from cihatbot.utils.timer import Timer
from configparser import ConfigParser
from typing import Callable


def inject_self(method: Callable) -> Callable:
    def wrapped(self, name) -> Module:
        module = method(self, name)
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
        timer = self.inject_timer("timer")
        trader = RealTrader(self.config, connector, timer).init()
        return trader

    @inject_self
    def inject_connector(self, name: str) -> Connector:
        connector = BinanceConnector().init()
        return connector

    @inject_self
    def inject_timer(self, name: str) -> Timer:
        timer = Timer(0.02).init()
        return timer


