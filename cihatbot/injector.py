from __future__ import annotations
import cihatbot.module


class Injector:

    def inject_app(self, name: str) -> cihatbot.module.Module:
        pass

    def inject_user(self, name: str) -> cihatbot.module.Module:
        pass

    def inject_ui(self, name: str) -> cihatbot.module.Module:
        pass

    def inject_parser(self, name: str) -> cihatbot.module.Module:
        pass

    def inject_trader(self, name: str) -> cihatbot.module.Module:
        pass

    def inject_connector(self, name: str) -> cihatbot.module.Module:
        pass
