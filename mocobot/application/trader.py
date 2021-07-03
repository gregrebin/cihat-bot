from mocobot.framework.module import Module
from mocobot.application.order import Order
from mocobot.application.market import Market
from mocobot.application.connector import Connector, TradeEvent, CandleEvent, UserEvent
from configparser import SectionProxy
from abc import abstractmethod
from typing import Dict, Callable, Type, Tuple
from collections import namedtuple


Submit = namedtuple("Submit", "uid eid")


class Trader(Module):

    TIMER_INTERVAL = 0.02

    def __init__(self, config: SectionProxy, category: Type, name: str):
        super().__init__(config, category, name)

    @property
    def events(self) -> Dict[Type, Callable]:
        return {
            TradeEvent: self.emit,
            CandleEvent: self.emit,
            UserEvent: self.emit
        }

    @abstractmethod
    def update(self, order: Order, market: Market) -> Tuple[Submit, ...]:
        pass

