from __future__ import annotations
from mocobot.framework.module import Module
from mocobot.application.ui import AddSessionEvent, ConfigEvent
from typing import List, Dict, Callable, Type
from configparser import SectionProxy


class Application(Module):

    def __init__(self, config: SectionProxy, category: Type, name: str) -> None:
        super().__init__(config, category, name)

    def pre_run(self) -> None:
        pass

    async def on_run(self) -> None:
        pass

    @property
    def events(self) -> Dict[Type, Callable]:
        return {
            AddSessionEvent: self._add_session_event,
            ConfigEvent: self._config_event
        }

    def _add_session_event(self, event: AddSessionEvent):
        self.log("Adding new session")
        self.add_submodule(self.injector.inject("session", event.session_name))

    def _config_event(self, event: ConfigEvent):
        self.log("Changing config")
        pass

    def on_stop(self) -> None:
        pass

    def post_run(self) -> None:
        pass

