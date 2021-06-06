from cihatbot.application.parser import Parser, InvalidString
from cihatbot.application.order import (
    ExecutionOrder,
    SingleExecutionOrder,
    ParallelExecutionOrder,
    SequentExecutionOrder,
    ExecutionConditions,
    ExecutionParams)
from typing import List
import re
import time


class CompleteParser(Parser):

    single_pattern = re.compile("(?P<command>buy|sell) (?P<symbol>[A-Z]+) (?P<price>[0-9]+[.][0-9]+) (?P<quantity>[0-9]+[.][0-9]+)")
    parallel_pattern = re.compile("\[p (?P<list>[A-Za-z0-9., \[\]]*)\]")
    sequent_pattern = re.compile("\[s (?P<list>[A-Za-z0-9., \[\]]*)\]")

    def parse(self, order_string: str) -> ExecutionOrder:

        order_string = order_string.lstrip().rstrip()

        single_match = self.single_pattern.fullmatch(order_string)
        parallel_match = self.parallel_pattern.fullmatch(order_string)
        sequent_match = self.sequent_pattern.fullmatch(order_string)

        if single_match:
            return SingleExecutionOrder(
                time.time(),
                ExecutionParams(
                    single_match.group("command"),
                    single_match.group("symbol"),
                    float(single_match.group("price")),
                    float(single_match.group("quantity"))
                ),
                ExecutionConditions()
            )

        elif parallel_match:
            orders_str = parallel_match.group("list")
            orders = []
            for order in CompleteParser._split_order_list(orders_str):
                orders.append(self.parse(order))
            return ParallelExecutionOrder(orders)

        elif sequent_match:
            orders_str = sequent_match.group("list")
            orders = []
            for order in CompleteParser._split_order_list(orders_str):
                orders.append(self.parse(order))
            return SequentExecutionOrder(orders)

        else:
            raise InvalidString(order_string)

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
