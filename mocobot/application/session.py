from __future__ import annotations
from mocobot.framework.module import Module
from mocobot.application.order import Order, Empty
from mocobot.application.ui import Ui, AddOrderEvent, CancelOrderEvent, AddSessionEvent, AddUiEvent, AddTraderEvent, AddConnectorEvent, ConfigEvent
from mocobot.application.trader import Trader
from mocobot.application.connector import Connector, UserEvent, TickerEvent, ExchangeEvent
from typing import List, Dict, Callable, Type
from configparser import SectionProxy


class Session(Module):

    def __init__(self, config: SectionProxy, category: Type, name: str) -> None:
        super().__init__(config, category, name)
        self.order: Order = Empty()
        # self.uis: List[Ui] = []
        # self.traders: List[Trader] = []
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
        self.add_submodule(self.injector.inject(Ui, event.ui_name))

    def _add_trader_event(self, event: AddTraderEvent):
        self.add_submodule(self.injector.inject(Trader, event.trader_name))

    def _add_connector_event(self, event: AddConnectorEvent):
        for trader in self.get_category(Trader):
            trader.add_connector(self.injector.inject(
                Connector, event.connector_name, username=event.connector_username, password=event.connector_password)
            )

    def _add_order_event(self, event: AddOrderEvent):
        self.order.add(event.order, event.mode)
        for trader in self.get_category(Trader):
            trader.add_order(self.order)

    def _cancel_order_event(self, event: CancelOrderEvent):
        for trader in self.get_category(Trader):
            trader.cancel_order(self.order)

    def _exchange_event(self, event: ExchangeEvent):
        # update market
        for trader in self.get_category(Trader):
            trader.exchange_update()  # pass market

    def _ticker_event(self, event: TickerEvent):
        # update market
        for trader in self.get_category(Trader):
            trader.ticker_update()  # pass market

    def _user_event(self, event: UserEvent):
        self.order.update(event.uid, event.status)
        for ui in self.get_category(Ui):
            ui.trades_update(self.order)

