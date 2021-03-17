from cihatbot.module import Module
from cihatbot.events import Event
from cihatbot.utils.execution_order import SequentExecutionOrder, ParallelExecutionOrder, SingleExecutionOrder, ExecutionConditions, ExecutionParams
from configparser import SectionProxy
from queue import Queue
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext
from threading import Event as ThreadEvent
from calendar import timegm
from typing import List, Optional
import time
import re


class Telegram(Module):

    """
    root = [dd.mm.yyyy hh:mm] SEQUENT_ACTIONS
    sequent_actions = PARALLEL_ACTIONS[ poi  ...]
    parallel_actions = {RIGHT_ACTION|LEFT_ACTION}[, {SHORT_RIGHT_ACTION|SHORT_LEFT_ACTION}, ...]
    right_action = {comprare|vendere} RIGHT_QUANTITY RIGHT_SYMBOL a PRICE LEFT_SYMBOL
    right_action = {comprare|vendere} RIGHT_SYMBOL a PRICE LEFT_SYMBOL per LEFT_QUANTITY LEFT_SYMBOL
    short_right_action = RIGHT_QUANTITY a PRICE
    short_left_action = a PRICE per LEFT_QUANTITY
    
    example = 25.03.2021 06:00 comprare 0.002 btc a 60000.0 usdt, 0.002 a 62000.0 poi vendere 0.004 btc a 70000.0 usdt
    """

    BUY_COMMAND = "comprare"
    SELL_COMMAND = "vendere"

    command = re.compile("^(?P<datetime>(\d\d\.\d\d\.\d\d\d\d \d\d:\d\d )?)(?P<sequent_actions>.+)$")
    datetime = re.compile("^(?P<day>\d\d)\.(?P<month>\d\d)\.(?P<year>\d\d\d\d) (?P<hour>\d\d):(?P<minute>\d\d)$")
    right_action = re.compile(
        "^(?P<command>comprare|vendere) (?P<right_quantity>\d+\.?\d*) (?P<right_symbol>[a-z]+) a (?P<price>\d+\.?\d*) (?P<left_symbol>[a-z]+)$")
    left_action = re.compile(
        "^(?P<command>comprare|vendere) (?P<right_symbol>[a-z]+) a (?P<price>\d+\.?\d*) (?P<left_symbol>[a-z]+) per (?P<left_quantity>\d+\.?\d*) (?=left_symbol)$")
    short_right_action = re.compile(
        "^(?P<right_quantity>\d+\.?\d*) a (?P<price>\d+\.?\d*)$")
    short_left_action = re.compile(
        "^a (?P<price>\d+\.?\d*) per (?P<left_quantity>\d+\.?\d*)$"
    )

    def __init__(self, config: SectionProxy, queue: Queue, exit_event: ThreadEvent):
        super().__init__(config, queue, exit_event)

        self.updater = Updater(config["token"])
        self.dispatcher = self.updater.dispatcher

        self.dispatcher.add_handler(MessageHandler(Filters.regex(Telegram.command), self.command_handler))
        self.dispatcher.add_handler(MessageHandler(Filters.text, self.message_handler))

    def pre_run(self) -> None:
        self.updater.start_polling()

    def post_run(self) -> None:
        self.updater.stop()

    def message_handler(self, update: Update, context: CallbackContext) -> None:
        update.message.reply_text("invalid command")

    def command_handler(self, update: Update, context: CallbackContext) -> None:
        match = Telegram.command.match(update.message.text)
        all_actions = []

        datetime = Telegram._get_datetime(match["datetime"])
        print(datetime)

        sequent_actions = match["sequent_actions"].split(" poi ")
        print(sequent_actions)

        for parallel_actions in sequent_actions:
            actions = parallel_actions.split(", ")
            all_actions.append(actions)
        print(all_actions)

        try:
            order = Telegram._make_sequent_order(all_actions, datetime)

        except Exception:
            update.message.reply_text("malformed command")
            return

        print(order)
        # self.emit_event(Event("EXECUTE", {
        #     "order": order
        # }))

    @staticmethod
    def _make_sequent_order(all_actions: List[List[str]], datetime: float) -> SequentExecutionOrder:
        parallel_orders = []
        for actions in all_actions:
            parallel_order = Telegram._make_parallel_order(actions, datetime)
            parallel_orders.append(parallel_order)
        return SequentExecutionOrder(parallel_orders)

    @staticmethod
    def _make_parallel_order(actions: List[str], datetime: float) -> ParallelExecutionOrder:
        single_orders = []
        first = None
        for action in actions:
            single_order = Telegram.make_single_order(action, first, datetime)
            single_orders.append(single_order)
        return ParallelExecutionOrder(single_orders)

    @staticmethod
    def make_single_order(action: str, first: Optional[SingleExecutionOrder], datetime: float) -> SingleExecutionOrder:

        right_match = Telegram.right_action.match(action)
        left_match = Telegram.left_action.match(action)
        short_right_match = None
        short_left_match = None

        if first:
            short_right_match = Telegram.short_right_action.match(action)
            short_left_match = Telegram.short_left_action.match(action)

        if right_match:
            return Telegram._from_right(right_match, datetime)
        elif left_match:
            return Telegram._from_left(left_match, datetime)
        elif short_right_match:
            return Telegram._from_short_right(short_right_match, first, datetime)
        elif short_left_match:
            return Telegram._from_short_left(short_left_match, first, datetime)
        else:
            raise Exception

    @staticmethod
    def _from_right(match: re.Match, datetime: float) -> SingleExecutionOrder:
        command = ExecutionParams.CMD_BUY
        if match["command"] == Telegram.SELL_COMMAND:
            command = ExecutionParams.CMD_SELL
        symbol = match["right_symbol"] + match["left_symbol"]
        price = int(match["price"])
        quantity = match["right_quantity"]
        return SingleExecutionOrder(
            ExecutionParams(command, symbol, price, quantity),
            ExecutionConditions(datetime)
        )

    @staticmethod
    def _from_left(match: re.Match, datetime: float) -> SingleExecutionOrder:
        command = ExecutionParams.CMD_BUY
        if match["command"] == Telegram.SELL_COMMAND:
            command = ExecutionParams.CMD_SELL
        symbol = match["right_symbol"] + match["left_symbol"]
        price = int(match["price"])
        quantity = price * int(match["left_quantity"])
        return SingleExecutionOrder(
            ExecutionParams(command, symbol, price, quantity),
            ExecutionConditions(datetime)
        )

    @staticmethod
    def _from_short_right(match: re.Match, first: SingleExecutionOrder, datetime: float) -> SingleExecutionOrder:
        command = first.params.command
        symbol = first.params.symbol
        price = int(match["price"])
        quantity = match["right_quantity"]
        return SingleExecutionOrder(
            ExecutionParams(command, symbol, price, quantity),
            ExecutionConditions(datetime)
        )

    @staticmethod
    def _from_short_left(match: re.Match, first: SingleExecutionOrder, datetime: float) -> SingleExecutionOrder:
        command = first.params.command
        symbol = first.params.symbol
        price = int(match["price"])
        quantity = price * int(match["left_quantity"])
        return SingleExecutionOrder(
            ExecutionParams(command, symbol, price, quantity),
            ExecutionConditions(datetime)
        )


    @staticmethod
    def _get_datetime(datetime: str) -> float:
        datetime_match = Telegram.datetime.match(datetime)
        if datetime_match:
            return timegm((
                int(datetime_match["day"]),
                int(datetime_match["month"]),
                int(datetime_match["year"]),
                int(datetime_match["hour"]),
                int(datetime_match["minute"]),
                0
            ))
        else:
            return time.time()

