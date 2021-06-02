from cihatbot.framework.module import Module
from cihatbot.framework.events import Event
from cihatbot.application.order import Order, Mode
from cihatbot.application.parser import Parser
from configparser import SectionProxy
from dataclasses import dataclass


class Ui(Module):

    def __init__(self, config: SectionProxy, parser: Parser):
        super().__init__(config)
        self.parser: Parser = parser

    def trades_update(self, order: Order):
        pass


@dataclass
class AddModuleEvent(Event):
    """ Fires app.add_session """
    session_name: str = ""
    trader_name: str = ""
    ui_name: str = ""


@dataclass
class ConfigEvent(Event):
    """ Fires app.config """
    pass


@dataclass
class AddOrderEvent(Event):
    """ Fires trader.add """
    order: Order
    mode: Mode


@dataclass
class CancelOrderEvent(Event):
    """ Fires trader.cancel """
    uid: str
