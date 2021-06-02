from cihatbot.framework.module import Module
from cihatbot.application.order import Order
from cihatbot.application.parser import Parser
from configparser import SectionProxy


class Ui(Module):

    def __init__(self, config: SectionProxy, parser: Parser):
        super().__init__(config)
        self.parser: Parser = parser

    def submitted(self, order: Order):
        pass

    def filled(self, order: Order):
        pass

    def rejected(self, order: Order):
        pass
