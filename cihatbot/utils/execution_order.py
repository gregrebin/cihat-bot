import re
from typing import List


class ExecutionOrder:

    CMD_BUY = "buy"
    CMD_SELL = "sell"

    def __init__(self, order_type: str):
        self.order_type: str = order_type
        self.order_id: int = 0

    def __str__(self):
        return f"{self.order_type} order"


class EmptyExecutionOrder(ExecutionOrder):

    def __init__(self):
        super().__init__("empty")


class SingleExecutionOrder(ExecutionOrder):

    def __init__(self, command: str, symbol: str, price: float, quantity: float):
        super().__init__("single")

        if command != ExecutionOrder.CMD_BUY or command != ExecutionOrder.CMD_SELL:
            command = ExecutionOrder.CMD_BUY

        self.command: str = command
        self.symbol: str = symbol
        self.price: float = price
        self.quantity: float = quantity

    def __str__(self):
        return f"{super.__str__(self)}: {self.command} {self.symbol} {self.price} {self.quantity}"


class MultipleExecutionOrder(ExecutionOrder):

    def __init__(self, order_type, orders: List[ExecutionOrder]):
        super().__init__(order_type)

        self.orders = orders

    def add_order(self, execution_order: ExecutionOrder):
        self.orders.append(execution_order)

    def remove_order(self, execution_order: ExecutionOrder):

        for order in self.orders:

            if order == execution_order:
                self.orders.remove(order)

            elif isinstance(order, MultipleExecutionOrder):
                order.remove_order(execution_order)


class ParallelExecutionOrder(MultipleExecutionOrder):

    def __init__(self, orders: List[ExecutionOrder]):
        super().__init__("parallel", orders)


class SequentExecutionOrder(MultipleExecutionOrder):

    def __init__(self, orders: List[ExecutionOrder]):
        super().__init__("sequent", orders)


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
                single_match.group("command"),
                single_match.group("symbol"),
                float(single_match.group("price")),
                float(single_match.group("quantity"))
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








