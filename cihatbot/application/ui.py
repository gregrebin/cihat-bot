from cihatbot.framework.module import Module
from cihatbot.framework.events import Event
from cihatbot.application.order import Order, Mode
from configparser import SectionProxy
from dataclasses import dataclass, field
from abc import abstractmethod
from typing import Dict, Callable


class Ui(Module):
    log_name = __name__

    def __init__(self, config: SectionProxy):
        super().__init__(config)
        self.events: Dict[str, Callable] = {}

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
    name: str = field(init=False, default="AddModuleEvent")


@dataclass
class ConfigEvent(Event):
    """ Fires app.config """
    name: str = field(init=False, default="ConfigEvent")


@dataclass
class AddOrderEvent(Event):
    """ Fires trader.add """
    order: Order
    mode: Mode
    name: str = field(init=False, default="AddOrderEvent")


@dataclass
class CancelOrderEvent(Event):
    """ Fires trader.cancel """
    uid: str
    name: str = field(init=False, default="CancelOrderEvent")
