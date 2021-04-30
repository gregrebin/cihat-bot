from cihatbot.events import EventEmitter, EventListener
from cihatbot.application.events import TimerEvent
from cihatbot.module import Module
from threading import Thread
import time


class Timer(Module):

    def __init__(self, interval: float) -> None:
        super().__init__({})
        self.interval: float = interval
        self.thread: Thread = Thread()
        self.is_running: bool = False

    def pre_run(self) -> None:
        self.is_running = True

        def run():
            while self.is_running:
                time.sleep(self.interval)
                self.emitter.emit(TimerEvent({}))

        self.thread = Thread(target=run)
        self.thread.start()

    def post_run(self) -> None:
        if self.is_running:
            self.is_running = False
            self.thread.join()

    @staticmethod
    def is_later_than(ref_time: float):
        return time.time() >= ref_time
