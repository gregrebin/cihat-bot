from cihatbot.module import Module
from configparser import SectionProxy
from queue import Queue
from telegram import Bot
from threading import Event as ThreadEvent


class Telegram(Module):

    def __init__(self, config: SectionProxy, queue: Queue, exit_event: ThreadEvent):
        super().__init__(config, queue, exit_event)

        self.bot = Bot(config["token"])
        print(self.bot.getMe())

