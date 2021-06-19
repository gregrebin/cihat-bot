from mocobot.framework.events import Event
from mocobot.application.events import (
    ConnectEvent,
    AddOrderEvent,
    CancelOrderEvent,
    ConnectedEvent,
    AddedEvent,
    DeletedEvent,
    SubmittedEvent,
    FilledEvent,
    CancelledEvent,
    RejectedEvent
)
from mocobot.application.ui import Ui
from mocobot.application.parser import Parser, InvalidString
from telegram import Update
from telegram.ext import Updater, CommandHandler, Filters, CallbackContext
from configparser import SectionProxy


HELP_MESSAGE = f"""
Welcome to Cihat bot!
User following commands to start trading:

/connect KEY SECRET
    please refer to the following guide: https://www.binance.com/en-NG/support/faq/360002502072
    if you skip this step your orders will be rejected

/exec SYMBOL buy QUANTITY at PRICE and sell PERCENTS at PRICE
    to buy and then sell
    example: /exec BTCBUSD buy 0.0002 at 55000 and sell 100% at 70000

/exec SYMBOL buy QUANTITY at PRICE, QUANTITY at PRICE and sell PERCENTS at PRICE
    to buy at multiple prices
    example: /exec BTCBUSD buy 0.0002 at 55000, 0.0003 at 50000 and sell 100% at 70000

Other commands such as /exec_after and /delete are to be documented.

Created by 
Grigoriy Rebinskiy
me@gregrebin.com """


class Telegram(Ui):

    name = __name__

    def __init__(self, config: SectionProxy, parser: Parser):
        super().__init__(config, parser)

        self.user = self.config["user"]
        self.updater = Updater(self.config["token"])
        self.dispatcher = self.updater.dispatcher
        self.bot = self.updater.bot

        if "chat_id" in self.config:
            self.chat_id = self.config["chat_id"]
        else:
            self.chat_id = None

    def pre_run(self) -> None:
        super().pre_run()
        self.dispatcher.add_handler(
            CommandHandler("help", self.help_handler, filters=Filters.user(username=self.user)))
        self.dispatcher.add_handler(
            CommandHandler("connect", self.connect_handler, filters=Filters.user(username=self.user)))
        self.dispatcher.add_handler(
            CommandHandler("exec", self.add_parallel_handler, filters=Filters.user(username=self.user)))
        self.dispatcher.add_handler(
            CommandHandler("exec_after", self.add_sequent_handler, filters=Filters.user(username=self.user)))
        self.dispatcher.add_handler(
            CommandHandler("delete", self.delete_handler, filters=Filters.user(username=self.user)))
        self.updater.start_polling()

    def help_handler(self, update: Update, _: CallbackContext) -> None:
        self._update_chat_id(update.message.chat_id)
        self._send_message(HELP_MESSAGE)

    def connect_handler(self, update: Update, _: CallbackContext):
        self._update_chat_id(update.message.chat_id)

        message = update.message.text.lstrip("/connect ")
        self.log("Received connect command")

        user, password = message.split()

        self.log(f"""Connect trader: {user} - {password}""")
        self.emit(ConnectEvent({"user": user, "password": password}))

    def add_parallel_handler(self, update: Update, _: CallbackContext) -> None:
        self._update_chat_id(update.message.chat_id)
        message = update.message.text.lstrip("/exec ")
        self._add_order(message, "parallel")

    def add_sequent_handler(self, update: Update, _: CallbackContext) -> None:
        self._update_chat_id(update.message.chat_id)
        message = update.message.text.lstrip("/exec_after ")
        self._add_order(message, "sequent")

    def _add_order(self, message: str, mode: str) -> None:
        self.log(f"""Received add message: {message}""")
        try:
            order = self.parser.parse(message)
        except InvalidString as invalid_string:
            self._send_message(f"""Invalid command: {invalid_string.order_string}""")
            return
        self.log(f"""New execution order: {order}""")
        self.emit(AddOrderEvent({"order": order, "mode": mode}))

    def delete_handler(self, update: Update, _: CallbackContext) -> None:
        self._update_chat_id(update.message.chat_id)
        order_id = update.message.text.lstrip("/delete ")
        self.log(f"""Received delete message: {order_id}""")
        self.emit(CancelOrderEvent({"order_id": order_id}))

    def _update_chat_id(self, chat_id: int):
        if not self.chat_id == chat_id:
            self.log(f"""Registering new chat id: {chat_id}""")
            self.chat_id = chat_id

    def on_event(self, event: Event) -> None:
        # super().on_event(event)
        if event.is_type(ConnectedEvent):
            self.notify_connected(event)
        elif event.is_type(AddedEvent):
            self.notify_added(event)
        elif event.is_type(DeletedEvent):
            self.notify_deleted(event)
        elif event.is_type(SubmittedEvent):
            self.notify_submitted(event)
        elif event.is_type(FilledEvent):
            self.notify_filled(event)
        elif event.is_type(CancelledEvent):
            self.notify_cancelled(event)
        elif event.is_type(RejectedEvent):
            self.notify_error(event)

    def notify_connected(self, event: Event) -> None:
        user = event.data["user"]
        self.log(f"""CONNECTED event: {user}""")
        self._send_message(f"""Connected to user: {user}""")

    def notify_added(self, event: Event) -> None:
        order = event.data["single"]
        self.log(f"""ADDED event: {order}""")
        self._send_message(f"""Added order: {order}""")

    def notify_deleted(self, event: Event) -> None:
        order_id = event.data["order_id"]
        self.log(f"""DELETED event: {order_id}""")
        self._send_message(f"""Deleted order: {order_id}""")

    def notify_submitted(self, event: Event) -> None:
        order = event.data["single"]
        self.log(f"""SUBMITTED event: {order}""")
        self._send_message(f"""Submitted order: {order}""")

    def notify_filled(self, event: Event) -> None:
        order = event.data["single"]
        self.log(f"""FILLED event: {order}""")
        self._send_message(f"""Filled order: {order}""")

    def notify_cancelled(self, event: Event) -> None:
        order = event.data["single"]
        self.log(f"""CANCELLED event: {order}""")
        self._send_message(f"""Cancelled order: {order}""")

    def notify_error(self, event: Event) -> None:
        order = event.data["order"]
        message = event.data["message"]
        self.log(f"""ERROR event: {order}""")
        self._send_message(f"""Error on order: {order} - {message}""")

    def _send_message(self, message: str):
        if self.chat_id:
            self.bot.send_message(self.chat_id, message)

    def post_run(self) -> None:
        super().post_run()
        self.updater.stop()

