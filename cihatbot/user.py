from __future__ import annotations
from cihatbot.module import Module
from cihatbot.logger import Logger
from cihatbot.scheduler import Scheduler
from cihatbot.events import Event, EventListener, AddUiEvent, AddTraderEvent
from cihatbot.ui.ui import Ui
from cihatbot.ui.telegram import Telegram
from cihatbot.parser.parser import Parser
from cihatbot.parser.complete_parser import CompleteParser
from cihatbot.parser.simple_parser import SimpleParser
from cihatbot.trader.trader import Trader
from cihatbot.trader.real import RealTrader
from cihatbot.connector.connector import Connector
from cihatbot.connector.binance import BinanceConnector
from configparser import ConfigParser
from typing import Type, Dict, List
import logging


""" Concrete ui implementation classes """
UIS: Dict[str, Type[Ui]] = {
    "telegram-ui": Telegram
}

PARSERS: Dict[str, Type[Parser]] = {
    "complete-parser": CompleteParser,
    "simple-parser": SimpleParser
}

""" Concrete trader implementation classes """
TRADERS: Dict[str, Type[Trader]] = {
    "real-trader": RealTrader
}

CONNECTORS: Dict[str, Type[Connector]] = {
    "binance-connector": BinanceConnector
}


class User(Module):

    def __init__(self, config: Dict) -> None:
        super().__init__(config, __name__)

        self.uis: List[Ui] = []
        self.traders: List[Trader] = []

        self.log(f"""New user initialized""")

    def add_ui(self, ui_name: str, parser_name: str, config: Dict = None) -> Ui:

        ui_class = UIS[ui_name]
        parser_class = PARSERS[parser_name]

        if not config:
            config = dict(self.default_config[ui_name])
        parser = parser_class()
        ui = ui_class(config, parser)

        for trader in self.traders:
            trader.add_listener(ui.listener)
            ui.add_listener(trader.listener)
        ui.add_listener(self.listener)
        ui.add_listener(self.app_listener)

        self.uis.append(ui)
        self.scheduler.schedule(ui)

        self.logger.log(logging.INFO, f"""Added {ui_name} with {parser_name}""")
        return ui

    def add_trader(self, trader_name: str, connector_name: str, config: Dict = None) -> Trader:

        trader_class = TRADERS[trader_name]
        connector_class = CONNECTORS[connector_name]

        if not config:
            config = dict(self.default_config[trader_name])
        connector = connector_class()
        trader = trader_class(config, connector)

        for ui in self.uis:
            ui.add_listener(trader.listener)
            trader.add_listener(ui.listener)
        trader.add_listener(self.listener)
        trader.add_listener(self.app_listener)

        self.traders.append(trader)
        self.scheduler.schedule(trader)

        self.logger.log(logging.INFO, f"""Added {trader_name} with {connector_name}""")
        return trader

    def run(self):

        self.scheduler.run()
        self.listener.listen(self.on_event)
        self.scheduler.stop()

    def on_event(self, event: Event) -> None:

        if event.is_type(AddTraderEvent):
            self.add_trader(event.data["trader_name"], event.data["connector_name"], event.data["config"])

        elif event.is_type(AddUiEvent):
            self.add_ui(event.data["ui_name"], event.data["parser_name"], event.data["config"])

    def stop(self):

        for ui in self.uis:
            ui.stop()
        for trader in self.traders:
            trader.stop()
        self.listener.is_running()
