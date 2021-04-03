from cihatbot.module import Module
from cihatbot.connector.connector import Connector
from configparser import SectionProxy
from queue import Queue
from threading import Event as ThreadEvent
from typing import Dict


class Trader(Module):

    def __init__(self, config: Dict, connector: Connector):
        super().__init__(config)

        self.connector: Connector = connector
