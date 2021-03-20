from cihatbot.module import Module
from cihatbot.connector.connector import Connector
from configparser import SectionProxy
from queue import Queue
from threading import Event as ThreadEvent


class Trader(Module):

    def __init__(self, config: SectionProxy, queue: Queue, exit_event: ThreadEvent, connector: Connector):
        super().__init__(config, queue, exit_event)

        self.connector: Connector = connector
