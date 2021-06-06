from cihatbot.framework.module import Module
from cihatbot.framework.events import Event
from cihatbot.application.order import Order
from cihatbot.application.connector import Connector
from configparser import SectionProxy
from abc import abstractmethod


class Trader(Module):
    log_name = __name__

    TIMER_INTERVAL = 0.02

    def __init__(self, config: SectionProxy):
        super().__init__(config)

    def on_event(self, event: Event) -> None:
        super().on_event(event)
        self.emit(event)

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
