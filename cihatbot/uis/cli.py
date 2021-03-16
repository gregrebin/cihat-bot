from cihatbot.events import Event
from cihatbot.module import Module
from cihatbot.utils.execution_order import Parser
from queue import Queue
from threading import Event as ThreadEvent


class Cli(Module):

    BOUGHT_EVENT = "BOUGHT"
    SOLD_EVENT = "SOLD"

    def __init__(self, config, queue: Queue, exit_event: ThreadEvent):
        super().__init__(config, queue, exit_event)
        self.parser: Parser = Parser()

    def loop(self, event: Event):
        if event.name == Cli.BOUGHT_EVENT:
            self.bought(event)
        elif event.name == Cli.SOLD_EVENT:
            self.sold(event)
        else:
            self.pull()

    def pull(self):
        cmd = input("cihatbot: ")
        event = self._parse_cmd(cmd)
        if event:
            self.emit_event(event)
        else:
            print("Invalid command")

    def bought(self, event: Event):
        print("bought")

    def sold(self, event: Event):
        print("sold")

    def _parse_cmd(self, cmd: str) -> Event:

        if cmd.startswith("connect "):
            args = cmd.lstrip("connect ").split()
            return Event("CONNECT", {
                "user": args[0],
                "password": args[1]
            })

        elif cmd.startswith("execute "):
            order = self.parser.parse(cmd.lstrip("execute "))
            return Event("EXECUTE", {
                "order": order
            })
