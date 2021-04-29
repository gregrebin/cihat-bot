from cihatbot.events import EventEmitter, EventListener
from cihatbot.application.events import TimerEvent
from threading import Thread
import time


class Timer:

    def __init__(self) -> None:
        self.emitter: EventEmitter = EventEmitter()
        self.thread: Thread = Thread()
        self.is_running: bool = False

    def add_listener(self, listener: EventListener) -> None:
        self.emitter.add_listener(listener)

    def start(self, interval: float):
        self.is_running = True

        def run():
            while self.is_running:
                time.sleep(interval)
                self.emitter.emit(TimerEvent({}))

        self.thread = Thread(target=run)
        self.thread.start()

    def stop(self):
        if self.is_running:
            self.is_running = False
            self.thread.join()

    @staticmethod
    def is_later_than(ref_time: float):
        return time.time() >= ref_time
