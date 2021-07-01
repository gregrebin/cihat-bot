from mocobot.framework.module import Module
from mocobot.application.order import Order
from mocobot.application.market import Market
from mocobot.application.connector import Connector, TradeEvent, CandleEvent, UserEvent
from configparser import SectionProxy
from abc import abstractmethod
from typing import Dict, Callable, Type


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
    def add_order(self, order: Order, market: Market) -> None:
        pass

    @abstractmethod
    def cancel_order(self, order: Order, market: Market) -> None:
        pass

    @abstractmethod
    def new_trade(self, order: Order, market: Market) -> None:
        pass

    @abstractmethod
    def new_candle(self, order: Order, market: Market) -> None:
        pass
