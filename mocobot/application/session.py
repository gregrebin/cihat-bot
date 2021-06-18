from __future__ import annotations
from mocobot.framework.module import Module
from mocobot.application.order import Order, Empty
from mocobot.application.ui import Ui, AddOrderEvent, CancelOrderEvent, AddSessionEvent, AddUiEvent, AddTraderEvent, AddConnectorEvent, ConfigEvent
from mocobot.application.trader import Trader
from mocobot.application.connector import UserEvent, TickerEvent, ExchangeEvent
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
            AddUiEvent.name: self._add_ui_event,
            AddTraderEvent.name: self._add_trader_event,
            AddConnectorEvent.name: self._add_connector_event,
            AddSessionEvent.name: self.emit,
            ConfigEvent.name: self.emit,
            AddOrderEvent.name: self._add_order_event,
            CancelOrderEvent.name: self._cancel_order_event,
            ExchangeEvent.name: self._exchange_event,
            TickerEvent.name: self._ticker_event,
            UserEvent.name: self._user_event
        }

    def _add_ui_event(self, event: AddUiEvent):
        self.add_ui(self.injector.inject("ui", event.ui_name))

    def _add_trader_event(self, event: AddTraderEvent):
        self.add_trader(self.injector.inject("trader", event.trader_name))

    def _add_connector_event(self, event: AddConnectorEvent):
        for trader in self.traders:
            trader.add_connector(self.injector.inject(
                "connector", event.connector_name, username=event.connector_username, password=event.connector_password)
            )

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
