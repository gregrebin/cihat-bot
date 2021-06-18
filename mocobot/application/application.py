from __future__ import annotations
from mocobot.framework.module import Module
from mocobot.application.ui import AddModuleEvent, ConfigEvent
from mocobot.application.session import Session
from typing import List, Dict, Callable
from configparser import SectionProxy


class Application(Module):
    log_name = __name__

    def __init__(self, config: SectionProxy) -> None:
        super().__init__(config)
        self.sessions: List[Session] = []
        self.events: Dict[str, Callable] = {
            AddModuleEvent.name: self._add_module_event,
            ConfigEvent.name: self._config_event
        }

    def _add_module_event(self, event: AddModuleEvent):
        self.add_session(self.injector.inject("session", event.session_name))

    def _config_event(self, event: ConfigEvent):
        self.config()

    def add_session(self, session: Session) -> None:
        self.sessions.append(session)
        self.add_submodule(session)

    def config(self):
        pass
