from cihatbot.parser.parser import Parser, InvalidString
from cihatbot.execution_order.execution_order import (
    ExecutionOrder,
    SingleExecutionOrder,
    ParallelExecutionOrder,
    SequentExecutionOrder,
    ExecutionConditions,
    ExecutionParams)
from typing import List
import time
import re
import calendar


class SimpleParser(Parser):
    """
    Input syntax:
    root = [DATETIME ]SYMBOL buy BUY_ORDER[, BUY_ORDER, ...] and sell SELL_ORDER[, SELL_ORDER, ...]
    datetime = DD.MM.YYYY HH:MM
    buy_order = {RIGHT_BUY_ORDER|LEFT_BUY_ORDER}
    right_buy_order = RIGHT_QUANTITY at PRICE
    left_buy_order = at PRICE for LEFT_QUANTITY
    sell_order = PERCENTAGE at PRICE

    Example:
    25.03.2021 06:00 BTCBUSD buy 0.0002 at 55000, 0.0002 at 57000, at 59000 for 10 and sell 70% at 65000, 30% at 70000
    """

    root_long = re.compile("^(?P<datetime>(\d\d\.\d\d\.\d\d\d\d \d\d:\d\d )?)(?P<symbol>[A-Z]+) (?P<primary_command>buy|sell) (?P<primary_orders>.+) and (?P<secondary_command>buy|sell) (?P<secondary_orders>.+)$")
    root_short = re.compile("^(?P<datetime>(\d\d\.\d\d\.\d\d\d\d \d\d:\d\d )?)(?P<symbol>[A-Z]+) (?P<primary_command>buy|sell) (?P<primary_orders>.+)$")

    def parse(self, order_string: str) -> ExecutionOrder:

        root_long_match = self.root_long.match(order_string)
        root_short_match = self.root_short.match(order_string)
        long = False
        if root_long_match:
            root_match = root_long_match
            long = True
        elif root_short_match:
            root_match = root_short_match
        else:
            raise InvalidString(order_string)

        datetime = self._get_datetime(root_match["datetime"])
        symbol = root_match["symbol"]

        primary_command = root_match["primary_command"]
        primary_orders_str = root_match["primary_orders"].split(", ")
        primary_orders = self._parse_primary_orders(primary_command, primary_orders_str, datetime, symbol)

        if not long:
            return ParallelExecutionOrder(primary_orders)

        secondary_command = root_match["secondary_command"]
        secondary_orders_str = root_long_match["secondary_orders"].split(", ")

        orders = []

        for primary_order in primary_orders:
            secondary_orders = self._parse_secondary_orders(secondary_command, secondary_orders_str, datetime, symbol, primary_order.params)
            orders.append(SequentExecutionOrder([
                primary_order,
                ParallelExecutionOrder(secondary_orders)
            ]))

        return ParallelExecutionOrder(orders)

    right_primary = re.compile("^(?P<right_quantity>\d+\.?\d*) at (?P<price>-?\d+\.?\d*)(?P<conditions>.*)$")
    left_primary = re.compile("^at (?P<price>-?\d+\.?\d*) for (?P<left_quantity>\d+\.?\d*)(?P<conditions>.*)$")

    def _parse_primary_orders(self, command_str: str, primary_orders_str: List[str], datetime: float, symbol: str) -> List[SingleExecutionOrder]:

        if command_str == "buy":
            command = ExecutionParams.CMD_BUY
        elif command_str == "sell":
            command = ExecutionParams.CMD_SELL
        else:
            raise InvalidString(command_str)

        primary_orders = []
        for order in primary_orders_str:

            right_match = self.right_primary.match(order)
            left_match = self.left_primary.match(order)

            if right_match:
                price = float(right_match["price"])
                quantity = float(right_match["right_quantity"])
                conditions = right_match["conditions"]
            elif left_match:
                price = float(left_match["price"])
                quantity = price * float(left_match["right_quantity"])
                conditions = left_match["conditions"]
            else:
                raise InvalidString(order)

            if conditions.startswith(" if "):
                execution_conditions = self._get_conditions(conditions)
            else:
                execution_conditions = ExecutionConditions()

            primary_orders.append(SingleExecutionOrder(
                datetime,
                ExecutionParams(command, symbol, price, quantity),
                execution_conditions
            ))

        return primary_orders

    secondary = re.compile("^(?P<percent>\d\d|100)% at (?P<price>\d+\.?\d*)(?P<conditions>.*)$")

    def _parse_secondary_orders(self, command_str: str, secondary_orders_str: List[str], datetime: float, symbol: str, primary_params: ExecutionParams) -> List[SingleExecutionOrder]:

        if command_str == "buy":
            command = ExecutionParams.CMD_BUY
        elif command_str == "sell":
            command = ExecutionParams.CMD_SELL
        else:
            raise InvalidString(command_str)

        secondary_orders = []
        for order in secondary_orders_str:

            secondary_match = self.secondary.match(order)
            if not secondary_match:
                raise InvalidString(order)

            price = float(secondary_match["price"])
            percent = float(secondary_match["percent"]) / 100
            quantity = primary_params.quantity * percent
            conditions = secondary_match["conditions"]

            if conditions.startswith(" if "):
                execution_conditions = self._get_conditions(conditions, primary_params)
            else:
                execution_conditions = ExecutionConditions()

            secondary_orders.append(SingleExecutionOrder(
                datetime,
                ExecutionParams(command, symbol, price, quantity),
                execution_conditions
            ))

        return secondary_orders

    conditions = re.compile("^ if price (?P<symbol>[<>]) (?P<price>(\d+\.?\d*)|(\d+%))$")

    def _get_conditions(self, conditions: str, reference: ExecutionParams = None) -> ExecutionConditions:

        conditions_match = self.conditions.match(conditions)
        if not conditions_match:
            raise InvalidString(conditions)

        symbol = conditions_match["symbol"]
        price_str = conditions_match["price"]

        if price_str.endswith("%"):
            price = float(price_str.rstrip("%"))
            ref = reference
        else:
            price = float(price_str)
            ref = None

        if symbol == "<":
            return ExecutionConditions(max_price=price, reference=ref)
        elif symbol == ">":
            return ExecutionConditions(min_price=price, reference=ref)
        else:
            raise InvalidString(symbol)

    datetime = re.compile("^(?P<day>\d\d)\.(?P<month>\d\d)\.(?P<year>\d\d\d\d) (?P<hour>\d\d):(?P<minute>\d\d) $")

    def _get_datetime(self, datetime: str) -> float:
        datetime_match = self.datetime.match(datetime)
        if datetime_match:
            return calendar.timegm((
                int(datetime_match["year"]),
                int(datetime_match["month"]),
                int(datetime_match["day"]),
                int(datetime_match["hour"]),
                int(datetime_match["minute"]),
                0
            ))
        else:
            return time.time()
