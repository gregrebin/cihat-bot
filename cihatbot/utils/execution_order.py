from __future__ import annotations
from typing import List, Callable
import re
import time


class ExecutionParams:

    CMD_BUY = "buy"
    CMD_SELL = "sell"

    def __init__(self, command: str, symbol: str, price: float, quantity: float) -> None:

        if not (command == ExecutionParams.CMD_BUY or command == ExecutionParams.CMD_SELL):
            command = ExecutionParams.CMD_BUY

        self.command: str = command
        self.symbol: str = symbol
        self.price: float = price
        self.quantity: float = quantity


class ExecutionConditions:

    def __init__(self, from_time: float):
        self.from_time: float = from_time


class ExecutionOrder:

    def __init__(self, order_type: str):
        self.order_type: str = order_type
        self.executed: float = False

    def __str__(self):
        return f'''{self.order_type} order'''

    def execute(self, execute_function: Callable[[SingleExecutionOrder], bool]):
        pass

    def add_parallel(self, execution_order: ExecutionOrder) -> ExecutionOrder:
        return ParallelExecutionOrder([execution_order])

    def add_sequential(self, execution_order: ExecutionOrder) -> ExecutionOrder:
        return SequentExecutionOrder([execution_order])

    def remove(self, execution_order: ExecutionOrder) -> ExecutionOrder:
        return EmptyExecutionOrder()


class EmptyExecutionOrder(ExecutionOrder):

    def __init__(self):
        super().__init__("empty")


class SingleExecutionOrder(ExecutionOrder):

    def __init__(self, execution_params: ExecutionParams, execution_conditions: ExecutionConditions):
        super().__init__("single")

        self.params: ExecutionParams = execution_params
        self.conditions: ExecutionConditions = execution_conditions

        self.order_id: int = 0

    def __str__(self):
        return f'''{self.params.command} {self.params.symbol} {self.params.price} {self.params.quantity}'''

    def execute(self, execute_function: Callable[[SingleExecutionOrder], bool]):
        if not self.executed:
            success = execute_function(self)
            self.executed = success

    def add_parallel(self, execution_order: ExecutionOrder) -> ExecutionOrder:
        return ParallelExecutionOrder([self, execution_order])

    def add_sequential(self, execution_order: ExecutionOrder) -> ExecutionOrder:
        return SequentExecutionOrder([self, execution_order])

    def remove(self, execution_order: ExecutionOrder) -> ExecutionOrder:
        if self == execution_order:
            return EmptyExecutionOrder()
        else:
            return self


class MultipleExecutionOrder(ExecutionOrder):

    def __init__(self, order_type, orders: List[ExecutionOrder]):
        super().__init__(order_type)

        self.orders = orders

    def __str__(self):
        return f'''[{self.order_type} {', '.join([str(order) for order in self.orders])}]'''

    def _check_executed(self):
        for order in self.orders:
            if not order.executed:
                return
        self.executed = True

    def remove(self, execution_order: ExecutionOrder) -> ExecutionOrder:

        if self == execution_order:
            return EmptyExecutionOrder()

        for index in range(len(self.orders)):
            order = self.orders[index].remove(execution_order)

            if isinstance(order, EmptyExecutionOrder):
                self.orders.pop(index)
            else:
                self.orders[index] = order

        return self


class ParallelExecutionOrder(MultipleExecutionOrder):

    def __init__(self, orders: List[ExecutionOrder]):
        super().__init__("parallel", orders)

    def execute(self, execute_function: Callable[[SingleExecutionOrder], bool]):
        for order in self.orders:
            order.execute(execute_function)
        self._check_executed()

    def add_parallel(self, execution_order: ExecutionOrder) -> ExecutionOrder:
        self.orders.append(execution_order)
        return self

    def add_sequential(self, execution_order: ExecutionOrder) -> ExecutionOrder:
        return SequentExecutionOrder([self, execution_order])


class SequentExecutionOrder(MultipleExecutionOrder):

    def __init__(self, orders: List[ExecutionOrder]):
        super().__init__("sequent", orders)

    def execute(self, execute_function: Callable[[SingleExecutionOrder], bool]):
        for order in self.orders:
            if not order.executed:
                order.execute(execute_function)
                break
        self._check_executed()

    def add_parallel(self, execution_order: ExecutionOrder) -> ExecutionOrder:
        return ParallelExecutionOrder([self, execution_order])

    def add_sequential(self, execution_order: ExecutionOrder) -> ExecutionOrder:
        self.orders.append(execution_order)
        return self


class Parser:

    single_pattern = re.compile("(?P<command>buy|sell) (?P<symbol>[A-Z]+) (?P<price>[0-9]+[.][0-9]+) (?P<quantity>[0-9]+[.][0-9]+)")
    parallel_pattern = re.compile("\[p (?P<list>[A-Za-z0-9., \[\]]*)\]")
    sequent_pattern = re.compile("\[s (?P<list>[A-Za-z0-9., \[\]]*)\]")

    @staticmethod
    def _split_order_list(order_list: str) -> List[str]:
        parenthesis = 0
        start = 0
        result_list = []
        for char in range(len(order_list)):
            if order_list[char] == "," and parenthesis == 0:
                result_list.append(order_list[start:char].lstrip().rstrip())
                start = char + 1
            elif order_list[char] == "[":
                parenthesis += 1
            elif order_list[char] == "]":
                parenthesis -= 1
        result_list.append(order_list[start:len(order_list)].lstrip().rstrip())
        return result_list

    def parse(self, order_description: str) -> ExecutionOrder:

        order_description = order_description.lstrip().rstrip()

        single_match = self.single_pattern.fullmatch(order_description)
        parallel_match = self.parallel_pattern.fullmatch(order_description)
        sequent_match = self.sequent_pattern.fullmatch(order_description)

        if single_match:
            return SingleExecutionOrder(
                ExecutionParams(
                    single_match.group("command"),
                    single_match.group("symbol"),
                    float(single_match.group("price")),
                    float(single_match.group("quantity"))
                ),
                ExecutionConditions(
                    time.time()
                )
            )

        elif parallel_match:
            orders_str = parallel_match.group("list")
            orders = []
            for order in Parser._split_order_list(orders_str):
                orders.append(self.parse(order))
            return ParallelExecutionOrder(orders)

        elif sequent_match:
            orders_str = sequent_match.group("list")
            orders = []
            for order in Parser._split_order_list(orders_str):
                orders.append(self.parse(order))
            return SequentExecutionOrder(orders)








