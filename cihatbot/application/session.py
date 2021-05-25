from __future__ import annotations
from cihatbot.framework.module import Module
from cihatbot.application.events import *
from cihatbot.application.execution_order import ExecutionOrder, EmptyExecutionOrder
from cihatbot.application.ui import Ui
from cihatbot.application.trader import Trader
from typing import List
from configparser import SectionProxy


class Session(Module):

    log_name = __name__

    def __init__(self, config: SectionProxy) -> None:
        super().__init__(config)
        self.execution_order: ExecutionOrder = EmptyExecutionOrder()
        self.uis: List[Ui] = []
        self.traders: List[Trader] = []
        self.log(f"""New session initialized""")

    def on_event(self, event: Event) -> None:
        super().on_event(event)

        if isinstance(event, AddOrderEvent):
            self.execution_order.add(event.order, event.mode)
            for trader in self.traders:
                trader.add(self.execution_order)

        elif isinstance(event, CancelOrderEvent):
            self.execution_order.cancel(event.order_id)
            for trader in self.traders:
                trader.cancel(self.execution_order)

        elif isinstance(event, SubmittedEvent):
            self.execution_order.submitted(event.order_id)
            for ui in self.uis:
                ui.submitted(self.execution_order)

        elif isinstance(event, FilledEvent):
            self.execution_order.filled(event.order_id)
            for ui in self.uis:
                ui.filled(self.execution_order)

        elif isinstance(event, RejectedEvent):
            self.execution_order.rejected(event.order_id)
            for ui in self.uis:
                ui.rejected(self.execution_order)

        elif isinstance(event, AddTraderEvent):
            self.add_trader(self.injector.inject_trader(event.trader_name))

        elif isinstance(event, AddUiEvent):
            self.add_ui(self.injector.inject_ui(event.ui_name))

        elif isinstance(event, AddSessionEvent) or isinstance(event, ConfigEvent):
            self.emit(event)

    def add_ui(self, ui: Ui):
        self.uis.append(ui)
        self.add_submodule(ui)
        self.log(f"""Added ui""")

    def add_trader(self, trader: Trader):
        self.traders.append(trader)
        self.add_submodule(trader)
        self.log(f"""Added trader""")

