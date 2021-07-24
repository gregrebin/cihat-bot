from mocobot.application.order import Order, Mode
from mocobot.application.market import Market
from mocobot.application.ui import Ui, AddConnectorEvent, AddOrderEvent, CancelOrderEvent
from asyncio import sleep, start_server, create_task
from configparser import SectionProxy
from typing import Type


class SocketUi(Ui):

    def post_init(self) -> None:
        self.server = None
        self.task = None
        self.order = None
        self.market = None

    def pre_run(self) -> None:
        pass

    async def on_run(self) -> None:
        self.server = await start_server(self._handler, '127.0.0.1', 8888)
        self.task = create_task(self.server.serve_forever())

    async def _handler(self, reader, writer) -> None:

        data = await reader.readline()
        message = data.decode().rstrip()

        command, _, content = str(message).partition(": ")
        self.log(f"""Command: {command}; content: {content}""")

        if command == "connector":
            connector = content.split()
            if len(connector) != 3:
                writer.write("Syntax should be\n connector: connector_name username password".encode())
            else:
                self.emit(AddConnectorEvent(connector[0], connector[1], connector[2]))

        elif command == "parallel":
            self.emit(AddOrderEvent(Order.parse(content), Mode.PARALLEL))

        elif command == "sequent":
            self.emit(AddOrderEvent(Order.parse(content), Mode.SEQUENT))

        elif command == "cancel":
            self.emit(CancelOrderEvent(content))

        elif command == "show":
            writer.write(str(self.order).encode())

        await writer.drain()
        writer.close()

    async def on_stop(self) -> None:
        self.task.cancel()
        self.server.close()

    def post_run(self) -> None:
        pass

    def update(self, order: Order, market: Market):
        self.order = order
        self.market = market


