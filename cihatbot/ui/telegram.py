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
    FILLED_EVENT = "FILLED"
    REJECTED_EVENT = "REJECTED"

    def __init__(self, config: SectionProxy, queue: Queue, exit_event: ThreadEvent, parser: Parser):
        super().__init__(config, queue, exit_event, parser)

        self.updater = Updater(self.config["token"])
        self.dispatcher = self.updater.dispatcher
        self.bot = self.updater.bot
        self.chat_id = None
        self.logger = Logger(__name__, logging.INFO)

        self.dispatcher.add_handler(CommandHandler("start", self.start_chat_handler))
        self.dispatcher.add_handler(MessageHandler(Filters.text, self.message_handler))

    def pre_run(self) -> None:
        self.updater.start_polling()

    def post_run(self) -> None:
        self.updater.stop()

    def loop(self, event: Event) -> None:
        if event.name == Telegram.FILLED_EVENT:
            self.notify_filled(event)
        elif event.name == Telegram.REJECTED_EVENT:
            self.notify_rejected(event)

    def start_chat_handler(self, update: Update, _: CallbackContext) -> None:
        self.logger.log(logging.INFO, "Received start command")
        chat_id = update.effective_chat.id
        if not self.chat_id:
            self.logger.log(logging.INFO, f"""Registering chat id: {chat_id}""")
            self.chat_id = chat_id

    def message_handler(self, update: Update, _: CallbackContext) -> None:

        message = update.message.text
        self.logger.log(logging.INFO, f"""Received message: {message}""")

        try:
            order = self.parser.parse(message)

        except InvalidString as invalid_string:
            self._send_message(f"""Invalid command: {invalid_string.order_string}""")
            return

        self.logger.log(logging.INFO, f"""New execution order: {order}""")
        self.emit_event(Event("EXECUTE", {
            "order": order
        }))

    def notify_filled(self, event: Event) -> None:
        order = event.data["single_order"]
        self.logger.log(logging.INFO, f"""FILLED event: {order}""")
        self._send_message(f"""Filled order: {order}""")

    def notify_rejected(self, event: Event) -> None:
        single_order = event.data["single"]
        all_orders = event.data["all"]
        self.logger.log(logging.INFO, f"""REJECTED EVENT: {single_order}""")
        self._send_message(f"""Rejected order: {single_order}\nRemaining: {all_orders}""")

    def _send_message(self, message: str):
        if self.chat_id:
            self.bot.send_message(self.chat_id, message)

