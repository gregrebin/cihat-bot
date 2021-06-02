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

    def submitted(self, order: Order):
        pass

    def filled(self, order: Order):
        pass

    def rejected(self, order: Order):
        pass


@dataclass
class AddSessionEvent(Event):
    """
    emitted by: ui
    handled by: app
    fires: app.add_session
    """
    session_name: str


@dataclass
class ConfigEvent(Event):
    """
    emitted by: ui
    handled by: app
    fires: app.config
    """
    pass


@dataclass
class AddTraderEvent(Event):
    """
    emitted by: ui
    handled by: session
    fires: session.add_trader
    """
    trader_name: str


@dataclass
class AddUiEvent(Event):
    """
    emitted by: ui
    handled by: session
    fires: session.add_ui
    """
    ui_name: str


@dataclass
class AddOrderEvent(Event):
    """
    emitted by: ui
    handled by: session
    fires: trader.add
    """
    order: Order
    mode: Mode


@dataclass
class CancelOrderEvent(Event):
    """
    emitted by: ui
    handled by: session
    fires: trader.cancel
    """
    uid: str
    data_fields = {"order_id"}
