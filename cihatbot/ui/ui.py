from cihatbot.module import Module
from cihatbot.parser.parser import Parser
from configparser import SectionProxy
from queue import Queue
from threading import Event as ThreadEvent
from typing import Dict


class Ui(Module):

    def __init__(self, config: Dict, queue: Queue, exit_event: ThreadEvent, parser: Parser):
        super().__init__(config, queue, exit_event)

        self.parser: Parser = parser
