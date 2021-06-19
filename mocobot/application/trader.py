from mocobot.framework.module import Module
from mocobot.application.order import Order
from mocobot.application.connector import Connector, ExchangeEvent, TickerEvent, UserEvent
from configparser import SectionProxy
from abc import abstractmethod
from typing import Dict, Callable, Type


class Trader(Module):

    TIMER_INTERVAL = 0.02

    def __init__(self, config: SectionProxy, category: Type, name: str):
        super().__init__(config, category, name)
        self.events: Dict[str, Callable] = {
            ExchangeEvent.name: self.emit,
            TickerEvent.name: self.emit,
            UserEvent.name: self.emit
        }

    def add_connector(self, connector: Connector) -> None:
        self.add_submodule(connector)

    @abstractmethod
    def add_order(self, order: Order) -> None:
        pass

    @abstractmethod
    def cancel_order(self, order: Order) -> None:
        pass

    @abstractmethod
    def exchange_update(self) -> None:
        pass

    @abstractmethod
    def ticker_update(self) -> None:
        pass
