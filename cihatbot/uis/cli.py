from cihatbot.ui import Ui
from typing import Dict

COMMANDS = {
    "buy": lambda cli: cli.emit_event("BUY"),
    "sell": lambda cli: cli.emit_event("SELL")
}


class Cli(Ui):

    def __init__(self, config):
        super().__init__(config)

    def run(self):
        cmd = input("cihatbot: ")
        COMMANDS[cmd](self)

    def bought(self, data: Dict[str, str]):
        print("bought")

    def sold(self, data: Dict[str, str]):
        print("sold")
