from __future__ import annotations
from typing import List, Callable


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
        return f"""{self.order_type} order"""

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
        return f"""{self.params.command} {self.params.symbol} {self.params.price} {self.params.quantity}"""

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

        if len(orders) == 0:
            raise EmptyOrderList

        self.orders = orders

    def __str__(self):
        orders = [str(order) for order in self.orders]
        return f"""[{self.order_type} {', '.join(orders)}]"""

    def _check_executed(self):
        for order in self.orders:
            if not order.executed:
                return
        self.executed = True

    def remove(self, execution_order: ExecutionOrder) -> ExecutionOrder:

        if self == execution_order:
            return EmptyExecutionOrder()

        new_orders = []

        for order in self.orders:
            new_order = order.remove(execution_order)
            if not isinstance(new_order, EmptyExecutionOrder):
                new_orders.append(new_order)

        if len(new_orders) == 0:
            return EmptyExecutionOrder()
        else:
            self.orders = new_orders
            return self


class ParallelExecutionOrder(MultipleExecutionOrder):

    def __init__(self, orders: List[ExecutionOrder]):
        super().__init__("parallel", orders)

    def execute(self, execute_function: Callable[[SingleExecutionOrder], bool]):
        if not self.executed:
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
        if not self.executed:
            self.orders[0].execute(execute_function)
        self._check_executed()

    def add_parallel(self, execution_order: ExecutionOrder) -> ExecutionOrder:
        return ParallelExecutionOrder([self, execution_order])

    def add_sequential(self, execution_order: ExecutionOrder) -> ExecutionOrder:
        self.orders.append(execution_order)
        return self


class EmptyOrderList(Exception):
    pass
