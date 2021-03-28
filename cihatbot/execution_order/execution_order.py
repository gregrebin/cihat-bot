from __future__ import annotations
from typing import List, Callable
from uuid import uuid4, UUID
from enum import Enum, auto


class OrderStatus(Enum):

    PENDING = auto()
    SUBMITTED = auto()
    REJECTED = auto()


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
        self.status: OrderStatus = OrderStatus.PENDING
        self.order_id: str = uuid4().hex
        self.external_id: int = 0

    def __str__(self):
        return f"""{self.order_type} order"""

    def add_parallel(self, execution_order: ExecutionOrder) -> ExecutionOrder:
        return execution_order

    def add_sequential(self, execution_order: ExecutionOrder) -> ExecutionOrder:
        return execution_order

    def remove(self, order_id: str = None, external_id: int = None) -> ExecutionOrder:
        return EmptyExecutionOrder()

    def call(self, func: Callable[[SingleExecutionOrder], None], order_id: str = None, external_id: int = None) -> bool:
        pass

    def submit(self, submit_func: Callable[[SingleExecutionOrder], OrderStatus]) -> None:
        pass

    def cancel(self, cancel_func: Callable[[SingleExecutionOrder], None], order_id: str = None, external_id: int = None) -> ExecutionOrder:
        return self.remove()

    def _is_order(self, order_id: str = None,  external_id: int = None):
        return self.order_id == order_id or self.external_id == external_id or (not order_id and not external_id)


class EmptyExecutionOrder(ExecutionOrder):

    def __init__(self):
        super().__init__("empty")


class SingleExecutionOrder(ExecutionOrder):

    def __init__(self, execution_params: ExecutionParams, execution_conditions: ExecutionConditions):
        super().__init__("single")

        self.params: ExecutionParams = execution_params
        self.conditions: ExecutionConditions = execution_conditions

    def __str__(self):
        return f"""{self.params.command} {self.params.symbol} {self.params.price} {self.params.quantity}"""

    def add_parallel(self, execution_order: ExecutionOrder) -> ExecutionOrder:
        return ParallelExecutionOrder([self, execution_order])

    def add_sequential(self, execution_order: ExecutionOrder) -> ExecutionOrder:
        return SequentExecutionOrder([self, execution_order])

    def remove(self, order_id: str = None,  external_id: int = None) -> ExecutionOrder:

        if self._is_order(order_id=order_id, external_id=external_id):
            return EmptyExecutionOrder()
        else:
            return self

    def call(self, func: Callable[[SingleExecutionOrder], None], order_id: str = None, external_id: int = None) -> bool:

        if self._is_order(order_id=order_id, external_id=external_id):
            func(self)
            return True
        else:
            return False

    def submit(self, submit_func: Callable[[SingleExecutionOrder], OrderStatus]) -> None:

        if self.status == OrderStatus.PENDING:
            self.status = submit_func(self)

    def cancel(self, cancel_func: Callable[[SingleExecutionOrder], None], order_id: str = None, external_id: int = None) -> ExecutionOrder:

        if not self._is_order(order_id=order_id, external_id=external_id):
            return self
        elif self.status == OrderStatus.SUBMITTED:
            cancel_func(self)
            return self
        else:
            return self.remove()


class MultipleExecutionOrder(ExecutionOrder):

    def __init__(self, order_type, orders: List[ExecutionOrder]):
        super().__init__(order_type)

        if len(orders) == 0:
            raise EmptyOrderList

        self.orders = orders

    def __str__(self):
        orders = [str(order) for order in self.orders]
        return f"""[{self.order_type} {', '.join(orders)}]"""

    def remove(self, order_id: str = None,  external_id: int = None) -> ExecutionOrder:

        if self._is_order(order_id=order_id, external_id=external_id):
            return EmptyExecutionOrder()

        new_orders = []
        empty = True
        for order in self.orders:
            new_order = order.remove(order_id, external_id)
            if not isinstance(new_order, EmptyExecutionOrder):
                new_orders.append(new_order)
                empty = False

        if empty:
            return EmptyExecutionOrder()
        else:
            self.orders = new_orders
            return self

    def call(self, func: Callable[[SingleExecutionOrder], None], order_id: str = None,  external_id: int = None) -> bool:
        applied = False
        for order in self.orders:
            applied = order.call(func, order_id=order_id, external_id=external_id) or applied
        return applied

    def cancel(self, cancel_func: Callable[[SingleExecutionOrder], None], order_id: str = None, external_id: int = None) -> ExecutionOrder:

        if self._is_order(order_id=order_id, external_id=external_id):
            self.cancel(cancel_func)
            return self.remove()

        new_orders = []
        empty = True
        for order in self.orders:
            new_order = order.cancel(cancel_func, order_id=order_id, external_id=external_id)
            if not isinstance(new_order, EmptyExecutionOrder):
                new_orders.append(new_order)
                empty = False

        if empty:
            return EmptyExecutionOrder()
        else:
            self.orders = new_orders
            return self

    def _check_submitted(self):
        for order in self.orders:
            if not order.status == OrderStatus.SUBMITTED:
                return
        self.status = OrderStatus.SUBMITTED


class ParallelExecutionOrder(MultipleExecutionOrder):

    def __init__(self, orders: List[ExecutionOrder]):
        super().__init__("parallel", orders)

    def add_parallel(self, execution_order: ExecutionOrder) -> ExecutionOrder:
        if isinstance(execution_order, ParallelExecutionOrder):
            self.orders.extend(execution_order.orders)
        else:
            self.orders.append(execution_order)
        self.status = OrderStatus.PENDING
        return self

    def add_sequential(self, execution_order: ExecutionOrder) -> ExecutionOrder:
        return SequentExecutionOrder([self, execution_order])

    def submit(self, submit_func: Callable[[SingleExecutionOrder], OrderStatus]):
        if not self.status == OrderStatus.SUBMITTED:
            for order in self.orders:
                order.submit(submit_func)
        self._check_submitted()


class SequentExecutionOrder(MultipleExecutionOrder):

    def __init__(self, orders: List[ExecutionOrder]):
        super().__init__("sequent", orders)

    def add_parallel(self, execution_order: ExecutionOrder) -> ExecutionOrder:
        return ParallelExecutionOrder([self, execution_order])

    def add_sequential(self, execution_order: ExecutionOrder) -> ExecutionOrder:
        if isinstance(execution_order, SequentExecutionOrder):
            self.orders.extend(execution_order.orders)
        else:
            self.orders.append(execution_order)
        self.status = OrderStatus.PENDING
        return self

    def submit(self, submit_func: Callable[[SingleExecutionOrder], OrderStatus]):
        if not self.status == OrderStatus.SUBMITTED:
            self.orders[0].submit(submit_func)
        self._check_submitted()


class EmptyOrderList(Exception):
    pass
