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

    def pre_run(self) -> None:
        pass

    async def on_run(self) -> None:
        pass

    @property
    def events(self) -> Dict[Type, Callable]:
        return {
            AddUiEvent: self._add_ui_event,
            AddTraderEvent: self._add_trader_event,
            AddConnectorEvent: self._add_connector_event,
            AddSessionEvent: self.emit,
            ConfigEvent: self.emit,
            AddOrderEvent: self._add_order_event,
            CancelOrderEvent: self._cancel_order_event,
            TradeEvent: self._trade_event,
            CandleEvent: self._candle_event,
            UserEvent: self._user_event
        }

    def _add_ui_event(self, event: AddUiEvent):
        self.log(f"""Adding new ui: {event.ui_name}""")
        self.add_submodule(self.injector.inject(Ui, event.ui_name))

    def _add_trader_event(self, event: AddTraderEvent):
        self.log(f"""Adding new trader: {event.trader_name}""")
        self.add_submodule(self.injector.inject(Trader, event.trader_name))

    def _add_connector_event(self, event: AddConnectorEvent):
        self.log(f"""Adding new connector: {event.connector_name}""")
        for trader in self.get_category(Trader):
            trader.add_submodule(self.injector.inject(
                Connector, event.connector_name, username=event.connector_username, password=event.connector_password)
            )

    def _add_order_event(self, event: AddOrderEvent):
        self.log(f"""Adding new order: {event.order}""")
        self.order = self.order.add(event.order, event.mode)
        self._update()

    def _cancel_order_event(self, event: CancelOrderEvent):
        self.log(f"""Cancelling order: {event.uid}""")
        self.order = self.order.update_status(event.uid, Status.CANCELLED)
        self._update()

    def _trade_event(self, event: TradeEvent):
        self.log(f"""New trade: {event.trade}""")
        self.market = self.market.trade(event.name, event.symbol, event.trade)
        self._update()

    def _candle_event(self, event: CandleEvent):
        self.log(f"""New candle: {event.candle}""")
        self.market = self.market.candle(event.name, event.symbol, event.interval, event.candle)
        self._update()

    def _user_event(self, event: UserEvent):
        self.log(f"""New user event: {event.uid} {event.status}""")
        self.order = self.order.update_status(uid=event.uid, eid=event.eid, status=event.status)
        self._update()

    def _update(self):
        for trader in self.get_category(Trader):
            submits = trader.update(self.order, self.market)
            for submit in submits:
                self.order = self.order.set_eid(submit.uid, submit.eid)
        for ui in self.get_category(Ui):
            ui.update(self.order, self.market)

    def on_stop(self) -> None:
        pass

    def post_run(self) -> None:
        pass

