from mocobot.framework.module import Module
from mocobot.framework.events import Event
from mocobot.application.order import Order, Mode
from mocobot.application.market import Market
from configparser import SectionProxy
from dataclasses import dataclass, field
from abc import abstractmethod
from typing import Dict, Callable, Type


class Ui(Module):

    def __init__(self, config: SectionProxy, category: Type, name: str):
        super().__init__(config, category, name)

    @property
    def events(self) -> Dict[Type, Callable]:
        return {}

    @property
    def static_site(self) -> str:
        return ""

    @abstractmethod
    def update(self, order: Order, market: Market):
        pass


@dataclass
class AddTraderEvent(Event):
    """ Fires app.add_session """
    trader_name: str


@dataclass
class AddUiEvent(Event):
    """ Fires session.add_ui """
    ui_name: str


@dataclass
class AddConnectorEvent(Event):
    """ Fires trader.add_connector """
    connector_name: str
    connector_username: str = ""
    connector_password: str = ""


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
