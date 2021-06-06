from __future__ import annotations
from threading import Lock
from typing import List, Callable, Dict, Tuple
from uuid import uuid4, UUID
from enum import Enum, auto
from dataclasses import dataclass, field, replace
from abc import ABC, abstractmethod


def new_uid():
    return uuid4().hex


class Status(Enum):
    NEW = auto()
    SUBMITTED = auto()
    CANCELLED = auto()
    FILLED = auto()
    REJECTED = auto()


class Command(Enum):
    BUY = auto()
    SELL = auto()


class Mode(Enum):
    PARALLEL = auto()
    SEQUENT = auto()


@dataclass(frozen=True)
class Order(ABC):

    status: Status = Status.NEW
    uid: str = field(default_factory=new_uid)

    @abstractmethod
    def add(self, order: Order, mode: Mode) -> Order:
        pass

    @abstractmethod
    def get(self, pending: bool = True) -> List[Order]:
        pass

    @abstractmethod
    def update(self, uid: str, status: Status) -> Order:
        pass

    def _add(self, order: Order, mode: Mode) -> Order:
        orders = self._add_term(mode) + order._add_term(mode)
        return Multiple(mode=mode, orders=orders)

    def _add_term(self, mode: Mode) -> Tuple[Order, ...]:
        return self,


@dataclass(frozen=True)
class Empty(Order):

    def add(self, order: Order, mode: Mode) -> Order:
        return order

    def get(self, pending: bool = True) -> List[Order]:
        return []

    def update(self, uid: str, status: Status) -> Order:
        return self


@dataclass(frozen=True)
class Single(Order):

    # TODO: implement multiple prices, think better about conditions

    eid: str = ""
    exchange: str = ""
    command: Command = Command.BUY
    symbol: str = ""
    quote: float = 0
    base: float = 0
    price: float = 0
    conditions: Dict[str, float] = field(default_factory=dict)

    def add(self, order: Order, mode: Mode) -> Order:
        return super()._add(order, mode)

    def get(self, pending: bool = True) -> List[Order]:
        if pending and self.status is not Status.NEW:
            return []
        return [self]

    def update(self, uid: str, status: Status) -> Order:
        if self.uid == uid:
            return replace(self, status=status)
        else:
            return self


@dataclass(frozen=True)
class Multiple(Order):

    mode: Mode = Mode.PARALLEL
    orders: Tuple[Order, ...] = field(default_factory=tuple)

    def add(self, order: Order, mode: Mode) -> Order:
        return super()._add(order, mode)

    def _add_term(self, mode: Mode) -> Tuple[Order, ...]:
        if self.mode is mode:
            return self.orders
        else:
            return self,

    def get(self, pending: bool = True) -> List[Order]:
        if pending and self.status is not Status.NEW:
            return []
        result = []
        for order in self.orders:
            orders = order.get(pending)
            result += orders
            if self.mode is Mode.SEQUENT and pending and orders:
                break
        return result

    def update(self, uid: str, status: Status) -> Order:
        if self.uid == uid:
            return replace(self, status=status)
        else:
            orders = tuple(order.update(uid, status) for order in self.orders)
            return replace(self, orders=orders)


# @dataclass(frozen=True)
# class Parallel(Multiple):
#
#     def add(self, order: Order) -> Order:
#         pass
#
#     def get(self, status: Status = None, uid: str = None, pending: bool = False) -> List[Order]:
#         pass
#
#     def update(self, status: Status) -> Order:
#         pass
#
#     def cancel(self, uid: str) -> Order:
#         pass
#
#
# @dataclass(frozen=True)
# class Sequent(Multiple):
#
#     def add(self, order: Order) -> Order:
#         pass
#
#     def get(self, status: Status = None, uid: str = None, pending: bool = False) -> List[Order]:
#         pass
#
#     def update(self, status: Status) -> Order:
#         pass
#
#     def cancel(self, uid: str) -> Order:
#         pass
#
#
# @dataclass(frozen=True)
# class Exclusive(Multiple):
#
#     def add(self, order: Order) -> Order:
#         pass
#
#     def get(self, status: Status = None, uid: str = None, pending: bool = False) -> List[Order]:
#         pass
#
#     def update(self, status: Status) -> Order:
#         pass
#
#     def cancel(self, uid: str) -> Order:
#         pass


def locked(no_lock: Callable):

    def with_lock(self: ExecutionOrder, *args, **kwargs):
        if self.lock.acquire():
            return_value = no_lock(self, *args, **kwargs)
            self.lock.release()
            return return_value

    return with_lock


class ExecutionOrder:

    def __init__(self, order_type: str):
        self.order_type: str = order_type
        self.status: OrderStatus = OrderStatus.PENDING
        self.order_id: str = uuid4().hex
        self.external_id: int = 0
        self.lock: Lock = Lock()

    def __str__(self):
        return f"""{self.order_type} order"""

    def add(self, order: ExecutionOrder, mode: str):
        pass

    def cancel(self, order_id: str):
        pass

    def submitted(self, order_id: str):
        pass

    def filled(self, order_id: str):
        pass

    def rejected(self, order_id: str):
        pass

    @locked
    def add_parallel(self, execution_order: ExecutionOrder) -> ExecutionOrder:
        return execution_order

    @locked
    def add_sequential(self, execution_order: ExecutionOrder) -> ExecutionOrder:
        return execution_order

    @locked
    def remove(self, order_id: str = None, external_id: int = None) -> ExecutionOrder:
        return EmptyExecutionOrder()

    @locked
    def call(self, func: Callable[[SingleExecutionOrder], None], order_id: str = None, external_id: int = None) -> bool:
        pass

    @locked
    def submit(self, submit_func: Callable[[SingleExecutionOrder], OrderStatus]) -> None:
        pass

    @locked
    def cancel(self, cancel_func: Callable[[SingleExecutionOrder], None], order_id: str = None, external_id: int = None) -> ExecutionOrder:
        return self.remove()

    def _is_order(self, order_id: str = None,  external_id: int = None):
        return self.order_id == order_id or self.external_id == external_id or (not order_id and not external_id)


class EmptyExecutionOrder(ExecutionOrder):

    def __init__(self):
        super().__init__("empty")


class SingleExecutionOrder(ExecutionOrder):

    def __init__(self, from_time: float, execution_params: ExecutionParams, execution_conditions: ExecutionConditions):
        super().__init__("single")

        self.from_time: float = from_time
        self.params: ExecutionParams = execution_params
        self.conditions: ExecutionConditions = execution_conditions

    def __str__(self):
        return f"""{self.params.command} {self.params.symbol} {self.params.price} {self.params.quantity}"""

    @locked
    def add_parallel(self, execution_order: ExecutionOrder) -> ExecutionOrder:
        return ParallelExecutionOrder([self, execution_order])

    @locked
    def add_sequential(self, execution_order: ExecutionOrder) -> ExecutionOrder:
        return SequentExecutionOrder([self, execution_order])

    @locked
    def remove(self, order_id: str = None,  external_id: int = None) -> ExecutionOrder:

        if self._is_order(order_id=order_id, external_id=external_id):
            return EmptyExecutionOrder()
        else:
            return self

    @locked
    def call(self, func: Callable[[SingleExecutionOrder], None], order_id: str = None, external_id: int = None) -> bool:

        if self._is_order(order_id=order_id, external_id=external_id):
            func(self)
            return True
        else:
            return False

    @locked
    def submit(self, submit_func: Callable[[SingleExecutionOrder], OrderStatus]) -> None:

        if self.status == OrderStatus.PENDING:
            self.status = submit_func(self)

    @locked
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

    @locked
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

    @locked
    def call(self, func: Callable[[SingleExecutionOrder], None], order_id: str = None,  external_id: int = None) -> bool:
        applied = False
        for order in self.orders:
            applied = order.call(func, order_id=order_id, external_id=external_id) or applied
        return applied

    @locked
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

    @locked
    def add_parallel(self, execution_order: ExecutionOrder) -> ExecutionOrder:
        if isinstance(execution_order, ParallelExecutionOrder):
            self.orders.extend(execution_order.orders)
        else:
            self.orders.append(execution_order)
        self.status = OrderStatus.PENDING
        return self

    @locked
    def add_sequential(self, execution_order: ExecutionOrder) -> ExecutionOrder:
        return SequentExecutionOrder([self, execution_order])

    @locked
    def submit(self, submit_func: Callable[[SingleExecutionOrder], OrderStatus]):
        if not self.status == OrderStatus.SUBMITTED:
            for order in self.orders:
                order.submit(submit_func)
        self._check_submitted()


class SequentExecutionOrder(MultipleExecutionOrder):

    def __init__(self, orders: List[ExecutionOrder]):
        super().__init__("sequent", orders)

    @locked
    def add_parallel(self, execution_order: ExecutionOrder) -> ExecutionOrder:
        return ParallelExecutionOrder([self, execution_order])

    @locked
    def add_sequential(self, execution_order: ExecutionOrder) -> ExecutionOrder:
        if isinstance(execution_order, SequentExecutionOrder):
            self.orders.extend(execution_order.orders)
        else:
            self.orders.append(execution_order)
        self.status = OrderStatus.PENDING
        return self

    @locked
    def submit(self, submit_func: Callable[[SingleExecutionOrder], OrderStatus]):
        if not self.status == OrderStatus.SUBMITTED:
            self.orders[0].submit(submit_func)
        self._check_submitted()


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

    def __init__(self, min_price: float = 0, max_price: float = 0, reference: ExecutionParams = None):
        self.min_p = min_price
        self.max_p = max_price
        self.reference = reference
        print(f"""initialized conditions: min {self.min_p}, max {self.max_p}, ref {self.reference}""")

    @staticmethod
    def _percent(f: float):
        return f / 100

    def max_price(self) -> float:
        if self.reference:
            return self._percent(self.max_p) * self.reference.price
        else:
            return self.max_p

    def min_price(self) -> float:
        print(f"""getting min price: min {self.min_p}, max {self.max_p}, ref {self.reference}""")
        if self.reference:
            print(f"""with ref: {self._percent(self.min_p) * self.reference.price}""")
            return self._percent(self.min_p) * self.reference.price
        else:
            print(f"""no ref: {self.min_p}""")
            return self.min_p


class EmptyOrderList(Exception):
    pass
