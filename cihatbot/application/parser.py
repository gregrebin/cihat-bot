from cihatbot.application.execution_order import (
    ExecutionOrder)


class Parser:

    def parse(self, order_string: str) -> ExecutionOrder:
        pass


class InvalidString(Exception):
    def __init__(self, order_string: str):
        self.order_string = order_string

