from cihatbot.ui import Ui
from cihatbot.events import Event
from cihatbot.order import Parser


class Cli(Ui):

    def __init__(self, config):
        super().__init__(config)

    @staticmethod
    def _parse_cmd(cmd: str) -> Event:

        if cmd.startswith("connect "):
            args = cmd.lstrip("connect ").split()
            return Event("CONNECT", {
                "user": args[0],
                "password": args[1]
            })

        elif cmd.startswith("execute "):
            parser = Parser()
            order = parser.parse(cmd.lstrip("execute "))
            return Event("EXECUTE", {
                "order": order
            })

    def run(self):
        cmd = input("cihatbot: ")
        event = Cli._parse_cmd(cmd)
        if event:
            self.emit_event(event)
        else:
            print("Invalid command")

    def bought(self, event: Event):
        print("bought")

    def sold(self, event: Event):
        print("sold")
