from cihatbot.framework.module import Module
from cihatbot.application.events import *
from cihatbot.application.execution_order import ExecutionOrder
from cihatbot.application.connector import Connector
from cihatbot.utils.timer import Timer
from configparser import SectionProxy


class Trader(Module):

    TIMER_INTERVAL = 0.02

    def __init__(self, config: SectionProxy, connector: Connector, timer: Timer):
        super().__init__(config)
        self.connector: Connector = connector
        self.add_submodule(self.connector)

    def on_event(self, event: Event) -> None:
        super().on_event(event)

        if event.is_type(TickerEvent):
            self.ticker()

        elif event.is_type(TimerEvent):
            self.timer()

    def ticker(self):
        pass

    def timer(self):
        pass

    def add(self, order: ExecutionOrder):
        pass

    def cancel(self, order: ExecutionOrder):
        pass
