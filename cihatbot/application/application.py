from __future__ import annotations
from cihatbot.framework.module import Module
from cihatbot.framework.events import Event
from cihatbot.application.ui import AddModuleEvent, ConfigEvent
from cihatbot.application.session import Session
from typing import List
from configparser import SectionProxy


class Application(Module):

    log_name = __name__

    def __init__(self, config: SectionProxy) -> None:
        super().__init__(config)
        self.sessions: List[Session] = []

    def on_event(self, event: Event) -> None:
        super().on_event(event)

        if isinstance(event, AddModuleEvent):
            self.add_session(self.injector.inject(Session, event.session_name))

        if isinstance(event, ConfigEvent):
            self.config()

    def add_session(self, session: Session) -> None:
        self.sessions.append(session)
        self.add_submodule(session)
        self.log("Created new session")

    def config(self):
        pass
