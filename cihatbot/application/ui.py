from cihatbot.framework.module import Module
from cihatbot.application.parser import Parser
from configparser import SectionProxy


class Ui(Module):

    def __init__(self, config: SectionProxy, parser: Parser):
        super().__init__(config)
        self.parser: Parser = parser
