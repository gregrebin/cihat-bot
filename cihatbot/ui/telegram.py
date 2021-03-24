from cihatbot.logger import Logger
from cihatbot.events import Event
from cihatbot.ui.ui import Ui
from cihatbot.parser.parser import Parser, InvalidString
from configparser import SectionProxy
from queue import Queue
from threading import Event as ThreadEvent
from telegram import Update
from telegram.ext import Updater, MessageHandler, CommandHandler, Filters, CallbackContext
import logging


class Telegram(Ui):

    BUY_COMMAND = "comprare"
    SELL_COMMAND = "vendere"
    CONNECTED_EVENT = "CONNECTED"
    ADDED_EVENT = "ADDED"
    DELETED_EVENT = "DELETED"
    SUBMITTED_EVENT = "SUBMITTED"
    FILLED_EVENT = "FILLED"

    def __init__(self, config: SectionProxy, queue: Queue, exit_event: ThreadEvent, parser: Parser):
        super().__init__(config, queue, exit_event, parser)

        self.user = self.config["user"]
        self.updater = Updater(self.config["token"])
        self.dispatcher = self.updater.dispatcher
        self.bot = self.updater.bot
        self.logger = Logger(__name__, logging.INFO)

        if "chat_id" in self.config:
            self.chat_id = self.config["chat_id"]
        else:
            self.chat_id = None

        self.dispatcher.add_handler(CommandHandler("start", self.start_chat_handler, filters=Filters.user(username=self.user)))
        self.dispatcher.add_handler(CommandHandler("connect", self.connect_handler, filters=Filters.user(username=self.user)))
        self.dispatcher.add_handler(CommandHandler("add_parallel", self.add_parallel_handler, filters=Filters.user(username=self.user)))
        self.dispatcher.add_handler(CommandHandler("add_sequent", self.add_sequent_handler, filters=Filters.user(username=self.user)))
        self.dispatcher.add_handler(CommandHandler("delete", self.delete_handler, filters=Filters.user(username=self.user)))

    def pre_run(self) -> None:
        self.updater.start_polling()

    def post_run(self) -> None:
        self.updater.stop()

    def loop(self, event: Event) -> None:
        if event.name == Telegram.CONNECTED_EVENT:
            self.notify_connected(event)
        elif event.name == Telegram.ADDED_EVENT:
            self.notify_added(event)
        elif event.name == Telegram.DELETED_EVENT:
            self.notify_deleted(event)
        elif event.name == Telegram.SUBMITTED_EVENT:
            self.notify_submitted(event)
        elif event.name == Telegram.FILLED_EVENT:
            self.notify_filled(event)

    def start_chat_handler(self, update: Update, _: CallbackContext) -> None:
        self.logger.log(logging.INFO, "Received start command")
        chat_id = update.effective_chat.id
        if not self.chat_id:
            self.logger.log(logging.INFO, f"""Registering chat id: {chat_id}""")
            self.chat_id = chat_id

    def connect_handler(self, update: Update, _: CallbackContext):

        message = update.message.text.lstrip("/connect ")
        self.logger.log(logging.INFO, "Received connect command")

        user, password = message.split()

        self.logger.log(logging.INFO, f"""Connect trader: {user} - {password}""")
        self.emit_event(Event("CONNECT", {
            "user": user,
            "password": password
        }))

    def add_parallel_handler(self, update: Update, _: CallbackContext) -> None:
        message = update.message.text.lstrip("/add_parallel ")
        self._add_order(message, "parallel")

    def add_sequent_handler(self, update: Update, _: CallbackContext) -> None:
        message = update.message.text.lstrip("/add_sequent ")
        self._add_order(message, "sequent")

    def _add_order(self, message: str, mode: str) -> None:
        self.logger.log(logging.INFO, f"""Received add message: {message}""")
        try:
            order = self.parser.parse(message)
        except InvalidString as invalid_string:
            self._send_message(f"""Invalid command: {invalid_string.order_string}""")
            return
        self.logger.log(logging.INFO, f"""New execution order: {order}""")
        self.emit_event(Event("ADD", {"order": order, "mode": mode}))

    def delete_handler(self, update: Update, _: CallbackContext) -> None:
        order_id = update.message.text.lstrip("/delete ")
        self.logger.log(logging.INFO, f"""Received delete message: {order_id}""")
        self.emit_event(Event("DELETE", {"order_id": order_id}))

    def notify_connected(self, event: Event) -> None:
        user = event.data["user"]
        self.logger.log(logging.INFO, f"""CONNECTED event: {user}""")
        self._send_message(f"""Connected to user: {user}""")

    def notify_added(self, event: Event) -> None:
        order = event.data["single"]
        self.logger.log(logging.INFO, f"""ADDED event: {order}""")
        self._send_message(f"""Added order: {order}""")

    def notify_deleted(self, event: Event) -> None:
        order_id = event.data["order_id"]
        self.logger.log(logging.INFO, f"""DELETED event: {order_id}""")
        self._send_message(f"""Deleted order: {order_id}""")

    def notify_submitted(self, event: Event) -> None:
        order = event.data["single"]
        self.logger.log(logging.INFO, f"""SUBMITTED event: {order}""")
        self._send_message(f"""Submitted order: {order}""")

    def notify_filled(self, event: Event) -> None:
        order = event.data["single"]
        self.logger.log(logging.INFO, f"""FILLED event: {order}""")
        self._send_message(f"""Filled order: {order}""")

    def _send_message(self, message: str):
        if self.chat_id:
            self.bot.send_message(self.chat_id, message)

