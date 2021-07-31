from asyncio import Task, Event, create_task
from typing import List, Coroutine, Callable


class Scheduler:

    def __init__(self):

        self.coroutines: List[Coroutine] = []
        self.tasks: List[Task] = []
        self.is_running: bool = False
        self.finish: Event = Event()

    def schedule(self, coroutine: Coroutine):

        self.coroutines.append(coroutine)
        if self.is_running:
            self._start(coroutine)

    async def run(self):

        for coroutine in self.coroutines:
            self._start(coroutine)
        self.is_running = True

        await self.finish.wait()
        self.is_running = False

    def _start(self, coroutine: Coroutine):

        task = create_task(coroutine)
        task.add_done_callback(self._done)
        self.tasks.append(task)

    def _done(self, task: Task):

        self.tasks.remove(task)
        if not self.tasks:
            self.finish.set()


