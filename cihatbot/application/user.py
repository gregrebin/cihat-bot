from __future__ import annotations
from cihatbot.module import Module
from cihatbot.events import Event, EventListener
from cihatbot.application.events import AddUiEvent, AddTraderEvent
from cihatbot.ui.ui import Ui
from cihatbot.trader.trader import Trader
from typing import Type, Dict, List
from configparser import SectionProxy
import logging


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
        self.logger.log(logging.INFO, f"""Added ui""")

    def add_trader(self, trader: Trader):
        self.traders.append(trader)
        self.add_submodule(trader)
        for ui in self.uis:
            trader.connect_module(ui)
        self.logger.log(logging.INFO, f"""Added trader""")

    def on_event(self, event: Event) -> None:
        if event.is_type(AddTraderEvent):
            self.add_trader(self.injector.inject_trader(event.data["trader-name"]))
        elif event.is_type(AddUiEvent):
            self.add_ui(self.injector.inject_ui(event.data["ui-name"]))

