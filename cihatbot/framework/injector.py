from __future__ import annotations
import cihatbot.framework.module
from configparser import ConfigParser


class Injector:

    def __init__(self, config: ConfigParser):
        self.config = config

    def inject_app(self, name: str) -> cihatbot.framework.module.Module:
        pass

    def inject_session(self, name: str) -> cihatbot.framework.module.Module:
        pass

    def inject_ui(self, name: str) -> cihatbot.framework.module.Module:
        pass

    def inject_parser(self, name: str) -> cihatbot.framework.module.Module:
        pass

    def inject_trader(self, name: str) -> cihatbot.framework.module.Module:
        pass

    def inject_connector(self, name: str) -> cihatbot.framework.module.Module:
        pass

