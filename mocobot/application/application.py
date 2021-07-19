from __future__ import annotations
from mocobot.framework.module import Module
from mocobot.application.ui import AddTraderEvent, ConfigEvent
from typing import List, Dict, Callable, Type
from configparser import SectionProxy


class Application(Module):

    def pre_run(self) -> None:
        pass

    async def on_run(self) -> None:
        pass

    @property
    def events(self) -> Dict[Type, Callable]:
        return {
            AddTraderEvent: self._add_trader_event,
            ConfigEvent: self._config_event
        }

    def _add_trader_event(self, event: AddTraderEvent):
        self.log("Adding new trader")
        self.add_submodule(self.injector.inject("trader", event.trader_name))

    def _config_event(self, event: ConfigEvent):
        self.log("Changing config")
        pass

    def on_stop(self) -> None:
        pass

    def post_run(self) -> None:
        pass

