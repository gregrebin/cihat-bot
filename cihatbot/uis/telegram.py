from cihatbot.module import Module
from configparser import SectionProxy
from queue import Queue
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext
from threading import Event as ThreadEvent


class Telegram(Module):

    def __init__(self, config: SectionProxy, queue: Queue, exit_event: ThreadEvent):
        super().__init__(config, queue, exit_event)

        self.updater = Updater(config["token"])
        self.dispatcher = self.updater.dispatcher
        self.message_handler = MessageHandler(Filters.text, self._message_handler)

        self.dispatcher.add_handler(self.message_handler)

    def pre_run(self) -> None:
        self.updater.start_polling()

    def post_run(self):
        self.updater.stop()

    def _message_handler(self, update: Update, context: CallbackContext):
        update.message.reply_text("ok")
