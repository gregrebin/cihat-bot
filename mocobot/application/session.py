from __future__ import annotations
from mocobot.framework.module import Module
from mocobot.application.order import Order, Empty, Status
from mocobot.application.market import Market
from mocobot.application.ui import Ui, AddOrderEvent, CancelOrderEvent, AddSessionEvent, AddUiEvent, AddTraderEvent, AddConnectorEvent, ConfigEvent
from mocobot.application.trader import Trader
from mocobot.application.connector import Connector, UserEvent, CandleEvent, TradeEvent
from typing import List, Dict, Callable, Type
from configparser import SectionProxy


class Session(Module):

    def __init__(self, config: SectionProxy, category: Type, name: str) -> None:
        super().__init__(config, category, name)
        self.order: Order = Empty()
        self.market: Market = Market()
        self.events: Dict[str, Callable] = {
            AddUiEvent.n: self._add_ui_event,
            AddTraderEvent.n: self._add_trader_event,
            AddConnectorEvent.n: self._add_connector_event,
            AddSessionEvent.n: self.emit,
            ConfigEvent.n: self.emit,
            AddOrderEvent.n: self._add_order_event,
            CancelOrderEvent.n: self._cancel_order_event,
            TradeEvent.n: self._trade_event,
            CandleEvent.n: self._candle_event,
            UserEvent.n: self._user_event
        }

    def _add_ui_event(self, event: AddUiEvent):
        self.add_submodule(self.injector.inject(Ui, event.ui_name))

    def _add_trader_event(self, event: AddTraderEvent):
        self.add_submodule(self.injector.inject(Trader, event.trader_name))

    def _add_connector_event(self, event: AddConnectorEvent):
        for trader in self.get_category(Trader):
            trader.add_submodule(self.injector.inject(
                Connector, event.connector_name, username=event.connector_username, password=event.connector_password)
            )

    def _add_order_event(self, event: AddOrderEvent):
        self.order = self.order.add(event.order, event.mode)
        for trader in self.get_category(Trader):
            trader.add_order(self.order, self.market)

    def _cancel_order_event(self, event: CancelOrderEvent):
        self.order = self.order.update(event.uid, Status.CANCELLED)
        for trader in self.get_category(Trader):
            trader.cancel_order(self.order, self.market)

    def _trade_event(self, event: TradeEvent):
        self.market = self.market.trade(event.name, event.symbol, event.trade)
        for trader in self.get_category(Trader):
            trader.new_trade(self.order, self.market)

    def _candle_event(self, event: CandleEvent):
        self.market = self.market.candle(event.name, event.symbol, event.interval, event.candle)
        for trader in self.get_category(Trader):
            trader.new_candle(self.order, self.market)

    def _user_event(self, event: UserEvent):
        self.order = self.order.update(event.uid, event.status)
        for ui in self.get_category(Ui):
            ui.trades_update(self.order)

