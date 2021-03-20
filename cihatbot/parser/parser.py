from cihatbot.execution_order.execution_order import (
    ExecutionOrder,
    SingleExecutionOrder,
    ParallelExecutionOrder,
    SequentExecutionOrder,
    ExecutionConditions,
    ExecutionParams)
from typing import List
import re
import time
import calendar


class Parser:

    def parse(self, order_string: str) -> ExecutionOrder:
        pass


class InvalidString(Exception):
    def __init__(self, order_string: str):
        self.order_string = order_string

