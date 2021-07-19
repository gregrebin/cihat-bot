from __future__ import annotations
from mocobot.framework.module import Module, InjectorException
from mocobot.application.order import Order, Empty, Status, Single
from mocobot.application.market import Market, Interval
from mocobot.application.ui import Ui, AddOrderEvent, CancelOrderEvent, AddTraderEvent, AddUiEvent, AddConnectorEvent, ConfigEvent
from mocobot.application.connector import Connector, UserEvent, CandleEvent
from typing import List, Dict, Callable, Type
from configparser import SectionProxy
import logging


class Trader(Module):

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
            AddConnectorEvent: self._add_connector_event,
            AddTraderEvent: self.emit,
            ConfigEvent: self.emit,
            AddOrderEvent: self._add_order_event,
            CancelOrderEvent: self._cancel_order_event,
            CandleEvent: self._candle_event,
            UserEvent: self._user_event
        }

    def _add_ui_event(self, event: AddUiEvent):
        self.log(f"""Adding new ui: {event.ui_name}""")
        try:
            ui = self.injector.inject(Ui, event.ui_name)
        except InjectorException as exception:
            self.log(str(exception), logging.ERROR)
            return
        self.add_submodule(ui)

    def _add_connector_event(self, event: AddConnectorEvent):
        self.log(f"""Adding new connector: {event.connector_name}""")
        try:
            connector = self.injector.inject(
                Connector, event.connector_name, username=event.connector_username, password=event.connector_password)
        except InjectorException as exception:
            self.log(str(exception), logging.ERROR)
            return
        self.add_submodule(connector)
        self._start_candles_on_connector(connector)

    def _add_order_event(self, event: AddOrderEvent):
        self.log(f"""Adding new order: {event.order}""")
        self.order = self.order.add(event.order, event.mode)
        self._start_candles_for_order(event.order)
        self._update()

    def _cancel_order_event(self, event: CancelOrderEvent):
        self.log(f"""Cancelling order: {event.uid}""")
        self.order = self.order.cancel(event.uid)
        self._update()

    def _candle_event(self, event: CandleEvent):
        self.log(f"""New candle: {event.name} {event.symbol} {event.interval} {event.candle}""")
        self.market = self.market.add_candle(event.name, event.symbol, event.interval, event.candle)
        self._update()

    def _user_event(self, event: UserEvent):
        self.log(f"""New user event: {event.uid} {event.status}""")
        self.order = self.order.update_status(uid=event.uid, eid=event.eid, status=event.status)
        self._update()

    def _update(self):
        for order in self.order.get():
            self._submit_order(order)
        for ui in self.get_submodule(Ui):
            ui.update(self.order, self.market)

    def _submit_order(self, order: Single):
        for indicator in order.indicators:
            dataframe = self.market[order.exchange, order.symbol, indicator.interval]
            if dataframe.empty or not indicator.check(dataframe): return
        for connector in self._get_connectors(order):
            eid = connector.submit(order)
            self.order.set_eid(order.uid, eid)

    def _start_candles_on_connector(self, connector: Connector):
        for single in self.order.get(pending=False):
            if single.exchange == connector.exchange:
                for indicator in single.indicators:
                    connector.start_candles(single.symbol, indicator.interval)

    def _start_candles_for_order(self, order: Order):
        for single in order.get(pending=False):
            for connector in self._get_connectors(single):
                for indicator in single.indicators:
                    connector.start_candles(single.symbol, indicator.interval)

    def _get_connectors(self, order: Single) -> List[Connector]:
        return self.get_submodule(Connector, exchange=order.exchange)

    def on_stop(self) -> None:
        pass

    def post_run(self) -> None:
        pass

