from asyncio import Task, create_task
from typing import List, Coroutine, Callable


class Scheduler:

    def __init__(self):

        self.coroutines: List[Coroutine] = []
        self.tasks: List[Task] = []
        self.is_running: bool = False

    def schedule(self, coroutine: Coroutine):

        self.coroutines.append(coroutine)
        if self.is_running:
            task = create_task(coroutine)
            self.tasks.append(task)

    async def run(self):

        for async_func in self.coroutines:
            task = create_task(async_func)
            self.tasks.append(task)
        self.is_running = True

        while len(self.tasks):
            task = self.tasks.pop()
            await task
        self.is_running = False


