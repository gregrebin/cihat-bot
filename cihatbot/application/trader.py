from cihatbot.framework.module import Module
from cihatbot.application.connector import Connector
from cihatbot.utils.timer import Timer
from configparser import SectionProxy


class Trader(Module):

    TIMER_INTERVAL = 0.02

    def __init__(self, config: SectionProxy, connector: Connector, timer: Timer):
        super().__init__(config)
        self.connector: Connector = connector
        self.add_submodule(self.connector)
        self.timer: Timer = timer
        self.add_submodule(self.timer)
