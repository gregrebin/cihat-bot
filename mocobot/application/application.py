from __future__ import annotations
from mocobot.framework.module import Module
from mocobot.application.ui import AddSessionEvent, ConfigEvent
from mocobot.application.session import Session
from typing import List, Dict, Callable
from configparser import SectionProxy


class Application(Module):

    def __init__(self, config: SectionProxy, log_name: str) -> None:
        super().__init__(config, log_name)
        self.sessions: List[Session] = []
        self.events: Dict[str, Callable] = {
            AddSessionEvent.name: self._add_session_event,
            ConfigEvent.name: self._config_event
        }

    def _add_session_event(self, event: AddSessionEvent):
        self.add_session(self.injector.inject("session", event.session_name))

    def _config_event(self, event: ConfigEvent):
        self.config()

    def add_session(self, session: Session) -> None:
        self.sessions.append(session)
        self.add_submodule(session)

    def config(self):
        pass
