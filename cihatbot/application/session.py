from __future__ import annotations
from cihatbot.framework.module import Module
from cihatbot.framework.events import Event
from cihatbot.application.order import Order, Empty, Status
from cihatbot.application.ui import Ui, AddOrderEvent, CancelOrderEvent, AddModuleEvent, ConfigEvent
from cihatbot.application.trader import Trader
from cihatbot.application.connector import Connector, UserEvent, TickerEvent, ExchangeEvent
from typing import List, Dict, Callable
from configparser import SectionProxy


class Session(Module):
    log_name = __name__

    def __init__(self, config: SectionProxy) -> None:
        super().__init__(config)
        self.order: Order = Empty()
        self.uis: List[Ui] = []
        self.traders: List[Trader] = []
        self.events: Dict[str, Callable] = {
            AddModuleEvent.name: self._add_module_event,
            ConfigEvent.name: self.emit,
            AddOrderEvent.name: self._add_order_event,
            CancelOrderEvent.name: self._cancel_order_event,
            ExchangeEvent.name: self._exchange_event,
            TickerEvent.name: self._ticker_event,
            UserEvent.name: self._user_event
        }

    def _add_module_event(self, event: AddModuleEvent):
        if event.ui_name:
            self.add_ui(self.injector.inject(Ui, event.ui_name))
        if event.trader_name:
            self.add_trader(self.injector.inject(Trader, event.trader_name))
        if event.connector_name and event.connector_username and event.connector_password:
            for trader in self.traders:
                trader.add_connector(self.injector.inject(Connector, event.connector_name,
                                                          username=event.connector_username,
                                                          password=event.connector_password))
        if event.session_name:
            self.emit(event)

    def _add_order_event(self, event: AddOrderEvent):
        self.order.add(event.order, event.mode)
        for trader in self.traders:
            trader.add_order(self.order)

    def _cancel_order_event(self, event: CancelOrderEvent):
        for trader in self.traders:
            trader.cancel_order(self.order)

    def _exchange_event(self, event: ExchangeEvent):
        # update market
        for trader in self.traders:
            trader.exchange_update()  # pass market

    def _ticker_event(self, event: TickerEvent):
        # update market
        for trader in self.traders:
            trader.ticker_update()  # pass market

    def _user_event(self, event: UserEvent):
        self.order.update(event.uid, event.status)
        for ui in self.uis:
            ui.trades_update(self.order)

    def add_ui(self, ui: Ui):
        self.uis.append(ui)
        self.add_submodule(ui)

    def add_trader(self, trader: Trader):
        self.traders.append(trader)
        self.add_submodule(trader)
