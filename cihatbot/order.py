import re
from typing import List


class ExecutionOrder:

    def __init__(self, order_type: str):
        self.order_type = order_type


class SingleExecutionOrder(ExecutionOrder):

    def __init__(self, command: str, symbol: str, price: float, quantity: float):
        super().__init__("single")

        self.command = command
        self.symbol = symbol
        self.price = price
        self.quantity = quantity


class MultipleExecutionOrder(ExecutionOrder):

    def __init__(self, order_type, orders: List[ExecutionOrder]):
        super().__init__(order_type)

        self.orders = orders


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








