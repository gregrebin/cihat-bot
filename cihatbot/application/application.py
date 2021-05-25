from __future__ import annotations
from cihatbot.framework.module import Module
from cihatbot.application.events import Event, AddSessionEvent, ConfigEvent
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

        if event.is_type(AddSessionEvent):
            self.add_session(self.injector.inject_session(event.data["session"]))

        if event.is_type(ConfigEvent):
            self.config()

    def add_session(self, session: Session) -> None:
        self.sessions.append(session)
        self.add_submodule(session)
        self.log("Created new session")

    def config(self):
        pass
