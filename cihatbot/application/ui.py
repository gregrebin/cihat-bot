from cihatbot.framework.module import Module
from cihatbot.framework.events import Event
from cihatbot.application.order import Order, Mode
from configparser import SectionProxy
from dataclasses import dataclass
from abc import abstractmethod


class Ui(Module):
    log_name = __name__

    def __init__(self, config: SectionProxy):
        super().__init__(config)

    @abstractmethod
    def trades_update(self, order: Order):
        pass


@dataclass
class AddModuleEvent(Event):
    """ Fires app.add_session, session.add_ui, session.add_trader, trader.add_connector """
    session_name: str = ""
    trader_name: str = ""
    connector_name: str = ""
    connector_username: str = ""
    connector_password: str = ""
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
