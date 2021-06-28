from __future__ import annotations
from mocobot.framework.module import Module
from mocobot.application.ui import AddSessionEvent, ConfigEvent
from typing import List, Dict, Callable, Type
from configparser import SectionProxy


class Application(Module):

    def __init__(self, config: SectionProxy, category: Type, name: str) -> None:
        super().__init__(config, category, name)
        self.events: Dict[str, Callable] = {
            AddSessionEvent.n: self._add_session_event,
            ConfigEvent.n: self._config_event
        }

    def _add_session_event(self, event: AddSessionEvent):
        self.add_submodule(self.injector.inject("session", event.session_name))

    def _config_event(self, event: ConfigEvent):
        pass

