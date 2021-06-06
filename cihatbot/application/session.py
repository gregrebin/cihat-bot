from __future__ import annotations
from cihatbot.framework.module import Module
from cihatbot.framework.events import Event
from cihatbot.application.order import Order, Empty, Status
from cihatbot.application.ui import Ui, AddOrderEvent, CancelOrderEvent, AddModuleEvent, ConfigEvent
from cihatbot.application.trader import Trader
from cihatbot.application.connector import Connector, UserEvent, TickerEvent, ExchangeEvent
from typing import List
from configparser import SectionProxy


class Session(Module):
    log_name = __name__

    def __init__(self, config: SectionProxy) -> None:
        super().__init__(config)
        self.order: Order = Empty()
        self.uis: List[Ui] = []
        self.traders: List[Trader] = []
        self.log(f"""New session initialized""")

    def on_event(self, event: Event) -> None:
        super().on_event(event)

        if isinstance(event, AddModuleEvent):
            if event.ui_name:
                self.add_ui(self.injector.inject(Ui, event.ui_name))
            if event.trader_name:
                self.add_trader(self.injector.inject(Trader, event.trader_name))
            if event.connector_name:
                for trader in self.traders:
                    trader.add_connector(self.injector.inject(Connector, event.connector_name))
            if event.session_name:
                self.emit(event)

        elif isinstance(event, ConfigEvent):
            self.emit(event)

        elif isinstance(event, AddOrderEvent):
            self.order.add(event.order, event.mode)
            for trader in self.traders:
                trader.add_order(self.order)

        elif isinstance(event, CancelOrderEvent):
            for trader in self.traders:
                trader.cancel_order(self.order)

        elif isinstance(event, ExchangeEvent):
            # update market
            for trader in self.traders:
                trader.exchange_update()  # pass market

        elif isinstance(event, TickerEvent):
            # update market
            for trader in self.traders:
                trader.ticker_update()  # pass market

        elif isinstance(event, UserEvent):
            self.order.update(event.uid, event.status)
            for ui in self.uis:
                ui.trades_update(self.order)

    def add_ui(self, ui: Ui):
        self.uis.append(ui)
        self.add_submodule(ui)
        self.log(f"""Added ui""")

    def add_trader(self, trader: Trader):
        self.traders.append(trader)
        self.add_submodule(trader)
        self.log(f"""Added trader""")
