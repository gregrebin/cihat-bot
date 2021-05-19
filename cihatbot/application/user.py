from __future__ import annotations
from cihatbot.framework.module import Module
from cihatbot.framework.events import Event
from cihatbot.application.events import AddUiEvent, AddTraderEvent
from cihatbot.application.ui import Ui
from cihatbot.application.trader import Trader
from typing import List
from configparser import SectionProxy


class User(Module):

    log_name = __name__

    def __init__(self, config: SectionProxy) -> None:
        super().__init__(config)
        self.uis: List[Ui] = []
        self.traders: List[Trader] = []
        self.log(f"""New user initialized""")

    def add_ui(self, ui: Ui):
        self.uis.append(ui)
        self.add_submodule(ui)
        for trader in self.traders:
            ui.connect_module(trader)
        self.log(f"""Added ui""")

    def add_trader(self, trader: Trader):
        self.traders.append(trader)
        self.add_submodule(trader)
        for ui in self.uis:
            trader.connect_module(ui)
        self.log(f"""Added trader""")

    def on_event(self, event: Event) -> None:
        # super().on_event(event)
        if event.is_type(AddTraderEvent):
            self.add_trader(self.injector.inject_trader(event.data["trader-name"]))
        elif event.is_type(AddUiEvent):
            self.add_ui(self.injector.inject_ui(event.data["ui-name"]))

