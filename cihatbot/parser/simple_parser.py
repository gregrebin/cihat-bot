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

    root = re.compile("^(?P<datetime>(\d\d\.\d\d\.\d\d\d\d \d\d:\d\d )?)(?P<symbol>[A-Z]+) buy (?P<buy_orders>.+) and sell (?P<sell_orders>.+)$")
    datetime = re.compile("^(?P<day>\d\d)\.(?P<month>\d\d)\.(?P<year>\d\d\d\d) (?P<hour>\d\d):(?P<minute>\d\d) $")
    right_buy = re.compile("^(?P<right_quantity>\d+\.?\d*) at (?P<price>\d+\.?\d*)$")
    left_buy = re.compile("^at (?P<price>\d+\.?\d*) for (?P<left_quantity>\d+\.?\d*)$")
    sell = re.compile("^(?P<percent>\d\d|100)% at (?P<price>\d+\.?\d*)$")

    def parse(self, order_string: str) -> ExecutionOrder:

        root_match = self.root.match(order_string)
        if not root_match:
            raise InvalidString(order_string)

        datetime = self._get_datetime(root_match["datetime"])
        symbol = root_match["symbol"]

        buy_orders_str = root_match["buy_orders"].split(", ")
        sell_orders_str = root_match["sell_orders"].split(", ")

        buy_orders = self._parse_buy_orders(buy_orders_str, datetime, symbol)
        orders = []

        for buy_order in buy_orders:
            sell_orders = self._parse_sell_orders(sell_orders_str, datetime, symbol, buy_order.params.quantity)
            orders.append(SequentExecutionOrder([
                buy_order,
                ParallelExecutionOrder(sell_orders)
            ]))

        return ParallelExecutionOrder(orders)

    def _parse_buy_orders(self, buy_orders_str: List[str], datetime: float, symbol: str) -> List[SingleExecutionOrder]:

        buy_orders = []
        for order in buy_orders_str:

            right_match = self.right_buy.match(order)
            left_match = self.left_buy.match(order)

            if right_match:
                price = float(right_match["price"])
                quantity = float(right_match["right_quantity"])
            elif left_match:
                price = float(right_match["price"])
                quantity = price * float(right_match["right_quantity"])
            else:
                raise InvalidString(order)

            buy_orders.append(SingleExecutionOrder(
                datetime,
                ExecutionParams(ExecutionParams.CMD_BUY, symbol, price, quantity),
                ExecutionConditions()
            ))

        return buy_orders

    def _parse_sell_orders(self, sell_orders_str: List[str], datetime: float, symbol: str, total_quantity: float) -> List[SingleExecutionOrder]:

        sell_orders = []
        for order in sell_orders_str:

            sell_match = self.sell.match(order)
            if not sell_match:
                raise InvalidString(order)

            price = float(sell_match["price"])
            percent = float(sell_match["percent"]) / 100
            quantity = total_quantity * percent

            sell_orders.append(SingleExecutionOrder(
                datetime,
                ExecutionParams(ExecutionParams.CMD_SELL, symbol, price, quantity),
                ExecutionConditions()
            ))

        return sell_orders

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
