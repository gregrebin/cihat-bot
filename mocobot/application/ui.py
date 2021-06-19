from mocobot.framework.module import Module
from mocobot.framework.events import Event
from mocobot.application.order import Order, Mode
from configparser import SectionProxy
from dataclasses import dataclass, field
from abc import abstractmethod
from typing import Dict, Callable, Type


class Ui(Module):

    def __init__(self, config: SectionProxy, category: Type, name: str):
        super().__init__(config, category, name)
        self.events: Dict[str, Callable] = {}

    @abstractmethod
    def trades_update(self, order: Order):
        pass


@dataclass
class AddSessionEvent(Event):
    """ Fires app.add_session """
    session_name: str = ""
    name: str = field(init=False, default="AddSessionEvent")


@dataclass
class AddUiEvent(Event):
    """ Fires session.add_ui """
    ui_name: str = ""
    name: str = field(init=False, default="AddUiEvent")


@dataclass
class AddTraderEvent(Event):
    """ Fires session.add_trader """
    trader_name: str = ""
    name: str = field(init=False, default="AddTraderEvent")


@dataclass
class AddConnectorEvent(Event):
    """ Fires trader.add_connector """
    connector_name: str = ""
    connector_username: str = ""
    connector_password: str = ""
    name: str = field(init=False, default="AddConnectorEvent")


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
