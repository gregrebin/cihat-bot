from cihatbot.module import Module
from cihatbot.connector.connector import Connector
from cihatbot.util.timer import Timer
from configparser import SectionProxy


class Trader(Module):

    TIMER_INTERVAL = 0.02

    def __init__(self, config: SectionProxy, connector: Connector):
        super().__init__(config)
        self.connector: Connector = connector
        self.timer: Timer = Timer(Trader.TIMER_INTERVAL)

    def pre_run(self) -> None:
        self.add_submodule(self.connector)
