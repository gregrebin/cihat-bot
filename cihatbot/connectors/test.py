from typing import Tuple

from cihatbot.application.connector import Connector
from cihatbot.application.order import SingleExecutionOrder


class TestConnector(Connector):

    def connect(self, key: str, secret: str) -> None:
        pass

    def satisfied(self, execution_order: SingleExecutionOrder) -> bool:
        pass

    def submit(self, execution_order: SingleExecutionOrder) -> Tuple[int, float]:
        pass

    def is_filled(self, execution_order: SingleExecutionOrder) -> bool:
        pass

    def cancel(self, execution_order: SingleExecutionOrder) -> None:
        pass
