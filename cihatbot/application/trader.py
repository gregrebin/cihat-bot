from cihatbot.framework.module import Module
from cihatbot.framework.events import Event
from cihatbot.application.order import Order
from cihatbot.application.connector import Connector
from configparser import SectionProxy


class Trader(Module):

    TIMER_INTERVAL = 0.02

    def __init__(self, config: SectionProxy, connector: Connector):
        super().__init__(config)
        self.connector: Connector = connector
        self.add_submodule(self.connector)

    def on_event(self, event: Event) -> None:
        super().on_event(event)
        self.emit(event)

    def add_order(self, order: Order):
        pass

    def cancel_order(self, order: Order):
        pass

    def exchange_update(self):
        pass

    def ticker_update(self):
        pass
