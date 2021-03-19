from cihatbot.module import Module
from cihatbot.events import Event
from cihatbot.utils.parser import Parser, SimpleParser, InvalidString
from configparser import SectionProxy
from queue import Queue
from telegram import Update
from telegram.ext import Updater, MessageHandler, CommandHandler, Filters, CallbackContext
from threading import Event as ThreadEvent


class Telegram(Module):

    BUY_COMMAND = "comprare"
    SELL_COMMAND = "vendere"
    FILLED_EVENT = "FILLED"
    REJECTED_EVENT = "REJECTED"

    def __init__(self, config: SectionProxy, queue: Queue, exit_event: ThreadEvent):
        super().__init__(config, queue, exit_event)

        self.updater = Updater(config["token"])
        self.dispatcher = self.updater.dispatcher
        self.bot = self.updater.bot
        self.chat_id = None
        self.parser: Parser = SimpleParser()

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
        if not self.chat_id:
            self.chat_id = update.effective_chat.id

    def message_handler(self, update: Update, _: CallbackContext) -> None:
        message = update.message.text

        try:
            order = self.parser.parse(message)

        except InvalidString as invalid_string:
            self._send_message(f"""Invalid command: {invalid_string.order_string}""")
            return

        self.emit_event(Event("EXECUTE", {
            "order": order
        }))

    def notify_filled(self, event: Event) -> None:
        self._send_message(f"""Filled order: {str(event.data["single_order"])}""")

    def notify_rejected(self, event: Event) -> None:
        self._send_message(f"""Rejected order: {event.data["single"]}\nRemaining: {event.data["all"]}""")

    def _send_message(self, message: str):
        if self.chat_id:
            self.bot.send_message(self.chat_id, message)

