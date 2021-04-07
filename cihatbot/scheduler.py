from threading import Thread
from typing import List


class Scheduler:

    def __init__(self):
        self.threads: List[Thread] = []
        self.is_running: bool = False

    def schedule(self, thread: Thread):
        self.threads.append(thread)
        if self.is_running:
            thread.start()

    def start(self):
        for thread in self.threads:
            thread.start()
        self.is_running = True

    def stop(self):
        for thread in self.threads:
            thread.join()
        self.is_running = False

