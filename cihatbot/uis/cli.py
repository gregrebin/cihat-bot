from cihatbot.ui import Ui
from cihatbot.events import Event
from typing import Dict, Tuple

COMMANDS = {
    "buy": lambda cli, data: cli.emit_event(Event("BUY", data)),
    "sell": lambda cli, data: cli.emit_event(Event("SELL", data))
}


class Cli(Ui):

    def __init__(self, config):
        super().__init__(config)

    def _parse_cmd(self, cmd: str) -> Tuple[str, Dict[str, str]]:
        parts = cmd.split()
        name = parts.pop(0)
        data = {}
        for entry in parts:
            entry_parts = entry.split("=")
            data[entry_parts[0]] = entry_parts[1]
        return name, data

    def _validate_data(self, data: Dict[str, str]) -> bool:
        return (
            "symbol" in data and
            "quantity" in data
        )

    def run(self):
        cmd = input("cihatbot: ")
        name, data = self._parse_cmd(cmd)
        if self._validate_data(data):
            COMMANDS[name](self, data)
        else:
            print("Invalid command")

    def bought(self, data: Dict[str, str]):
        print("bought")

    def sold(self, data: Dict[str, str]):
        print("sold")
