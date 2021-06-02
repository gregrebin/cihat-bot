from cihatbot.framework.module import Module
from cihatbot.framework.events import Event
from cihatbot.application.order import Order
from cihatbot.application.connector import Connector
from cihatbot.utils.timer import Timer
from dataclasses import dataclass
from configparser import SectionProxy


class Trader(Module):

    TIMER_INTERVAL = 0.02

    def __init__(self, config: SectionProxy, connector: Connector, timer: Timer):
        super().__init__(config)
        self.connector: Connector = connector
        self.add_submodule(self.connector)

    def on_event(self, event: Event) -> None:
        super().on_event(event)

        if isinstance(event, TickerEvent):
            self.ticker()

        elif isinstance(event, TimerEvent):
            self.timer()

    def ticker(self):
        pass

    def timer(self):
        pass

    def add(self, order: Order):
        pass

    def cancel(self, order: Order):
        pass


@dataclass
class TickerEvent(Event):
    """
    emitted by: connector
    handled by: trader
    fires: trader.ticker
    """


@dataclass
class TimerEvent(Event):
    """
    emitted by: connector
    handled by: trader
    fires: trader.timer
    """


@dataclass
class SubmittedEvent(Event):
    """
    emitted by: connector
    handled by: session
    fires: ui.submitted
    """
    uid: str


@dataclass
class FilledEvent(Event):
    """
    emitted by: connector
    handled by: session
    fires: ui.filled
    """
    uid: str


@dataclass
class RejectedEvent(Event):
    """
    emitted by: connector
    handled by: session
    fires: ui.rejected
    """
    uid: str

