from cihatbot.framework.module import Module
from cihatbot.application.events import UiEvent
from cihatbot.application.execution_order import ExecutionOrder
from cihatbot.application.parser import Parser
from configparser import SectionProxy


class Ui(Module):

    def __init__(self, config: SectionProxy, parser: Parser):
        super().__init__(config)
        self.parser: Parser = parser

    def submitted(self, order: ExecutionOrder):
        pass

    def filled(self, order: ExecutionOrder):
        pass

    def rejected(self, order: ExecutionOrder):
        pass
