from mocobot.application.order import Order, Mode, parse
from mocobot.application.ui import Ui, AddTraderEvent, AddConnectorEvent, AddOrderEvent, CancelOrderEvent
from asyncio import sleep, start_server, create_task
from configparser import SectionProxy
from typing import Type


class SocketUi(Ui):

    def __init__(self, config: SectionProxy, category: Type, name: str):
        super().__init__(config, category, name)
        self.server = None
        self.task = None
        self.order = None

    def pre_run(self) -> None:
        pass

    async def on_run(self) -> None:
        self.server = await start_server(self._handler, '127.0.0.1', 8888)
        self.task = create_task(self.server.serve_forever())

    async def _handler(self, reader, writer) -> None:

        data = await reader.readline()
        message = data.decode().rstrip()

        command, _, content = str(message).partition(": ")
        self.log(f"""Command: {command}, content: {content}""")

        if command == "trader":
            self.emit(AddTraderEvent(content))
        elif command == "connector":
            connector = content.split()
            if len(connector) != 3:
                writer.write("Syntax should be\n connector: name username password".encode())
            else:
                self.emit(AddConnectorEvent(connector[0], connector[1], connector[2]))
        elif command == "new":
            self.emit(AddOrderEvent(parse(content), Mode.PARALLEL))
        elif command == "cancel":
            self.emit(CancelOrderEvent(content))
        elif command == "show":
            writer.write(str(self.order).encode())

        await writer.drain()
        writer.close()

    def on_stop(self) -> None:
        self.task.cancel()
        self.server.close()

    def post_run(self) -> None:
        pass

    def update(self, order: Order):
        self.order = order


