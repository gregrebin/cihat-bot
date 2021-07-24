from __future__ import annotations
from mocobot.framework.module import Module, InjectorException, Event
from mocobot.application.order import Order, Empty, Status, Single
from mocobot.application.market import Market, Interval
from mocobot.application.ui import Ui, AddOrderEvent, CancelOrderEvent, AddTraderEvent, AddUiEvent, AddConnectorEvent, ConfigEvent
from mocobot.application.connector import Connector, UserEvent, CandleEvent
from asyncio import sleep
from time import time
from dataclasses import dataclass
from typing import List, Dict, Callable, Type, Tuple, Any
from configparser import SectionProxy
import logging


class Trader(Module):

    def __init__(self, config: SectionProxy, category: Type, name: str) -> None:
        super().__init__(config, category, name)
        self.order: Order = Empty()
        self.market: Market = Market()
        self.market_start: Dict[Tuple[str, Interval], Any] = {}
        self.time: int = int(time())

    def post_init(self) -> None:
        self._add_timer()

    def _add_timer(self) -> None:
        self.add_submodule(Timer().init())

    def pre_run(self) -> None:
        pass

    async def on_run(self) -> None:
        pass

    @property
    def events(self) -> Dict[Type, Callable]:
        return {
            AddUiEvent: self.add_ui_event,
            AddConnectorEvent: self.add_connector_event,
            AddTraderEvent: self.emit,
            ConfigEvent: self.emit,
            AddOrderEvent: self.add_order_event,
            CancelOrderEvent: self.cancel_order_event,
            CandleEvent: self.candle_event,
            UserEvent: self.user_event,
            TimerEvent: self.timer_event,
        }

    def add_ui_event(self, event: AddUiEvent):
        self.log(f"""Adding new ui: {event.ui_name}""")
        try:
            ui = self.injector.inject(Ui, event.ui_name)
        except InjectorException as exception:
            self.log(str(exception), logging.ERROR)
            return
        self.add_submodule(ui)

    def add_connector_event(self, event: AddConnectorEvent):
        self.log(f"""Adding new connector: {event.connector_name}""")
        try:
            connector = self.injector.inject(
                Connector, event.connector_name, username=event.connector_username, password=event.connector_password)
        except InjectorException as exception:
            self.log(str(exception), logging.ERROR)
            return
        self.add_submodule(connector)
        self._start_candles_on_connector(connector)

    def _start_candles_on_connector(self, connector: Connector):
        for single in self.order.get(pending=False):
            if single.exchange == connector.exchange:
                for indicator in single.indicators:
                    connector.start_candles(single.symbol, indicator.interval)

    def add_order_event(self, event: AddOrderEvent):
        self.log(f"""Adding new order: {event.order}""")
        self.order = self.order.add(event.order, event.mode)
        self._start_candles_for_order(event.order)
        self.time = self._start_timer(event.order)
        self._update()

    def _start_candles_for_order(self, order: Order):
        for single in order.get(pending=False):
            for connector in self._get_connectors(single):
                for indicator in single.indicators:
                    connector.start_candles(single.symbol, indicator.interval)

    def _start_timer(self, order: Order) -> int:
        now = time()
        for single in order.get(pending=False):
            if single.time > now:
                self._get_timer().set_timer(single.time)
        return int(now)

    def _get_timer(self) -> Timer:
        return self.get_submodule(Timer)[0]

    def cancel_order_event(self, event: CancelOrderEvent):
        self.log(f"""Cancelling order: {event.uid}""")
        self.order = self.order.cancel(event.uid)
        self._update()

    def candle_event(self, event: CandleEvent):
        self.log(f"""New candle: {event.exchange} {event.symbol} {event.interval} {event.candle}""")
        self.market = self.market.add_candle(event.exchange, event.symbol, event.interval, event.candle)
        self._update()

    def user_event(self, event: UserEvent):
        self.log(f"""New user event: {event.uid} {event.status}""")
        self.order = self.order.update_status(uid=event.uid, eid=event.eid, status=event.status)
        self._update()

    def timer_event(self, event: TimerEvent):
        self.log(f"Timer: {event.time}")
        self.time = event.time
        self._update()

    def _update(self):
        for order in self.order.get():
            if order.status is Status.NEW:
                self._submit_order(order)
            elif order.status is Status.SUBMITTED and order.to_cancel:
                self._cancel_order(order)
        for ui in self.get_submodule(Ui):
            ui.update(self.order, self.market)

    def _submit_order(self, order: Single):
        if order.time > self.time: return
        for indicator in order.indicators:
            dataframe = self.market[order.exchange, order.symbol, indicator.interval]
            if dataframe.empty: return
            start = self.market_start.setdefault((order.uid, indicator.interval), dataframe.index[-1])
            if not indicator.check(dataframe, start): return
        for connector in self._get_connectors(order):
            recipe = connector.submit(order)
            self.order = self.order.set_eid(order.uid, recipe.eid)
            self.order = self.order.update_status(order.uid, recipe.eid, recipe.status)

    def _cancel_order(self, order: Single):
        for connector in self._get_connectors(order):
            recipe = connector.cancel(order)
            self.order = self.order.update_status(order.uid, recipe.eid, recipe.status)

    def _get_connectors(self, order: Single) -> List[Connector]:
        return self.get_submodule(Connector, exchange=order.exchange)

    async def on_stop(self) -> None:
        pass

    def post_run(self) -> None:
        pass


class Timer(Module):

    def __init__(self):
        super().__init__({}, Timer, "timer")

    def pre_run(self) -> None:
        pass

    async def on_run(self) -> None:
        pass

    def set_timer(self, target: int) -> None:
        async def timer():
            now = time()
            if target > now:
                await sleep(target - now)
            self.emit(TimerEvent(target))
        self.scheduler.schedule(timer())

    @property
    def events(self) -> Dict[Type, Callable]:
        return {}

    async def on_stop(self) -> None:
        pass

    def post_run(self) -> None:
        pass


@dataclass
class TimerEvent(Event):
    time: int
