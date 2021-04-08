from asyncio import Task, create_task
from typing import List, Coroutine, Callable


class Scheduler:

    def __init__(self):
        self.async_funcs: List[Callable[[], Coroutine]] = []
        self.tasks: List[Task] = []
        self.is_running: bool = False

    def schedule(self, async_func: Callable[[], Coroutine]):
        self.async_funcs.append(async_func)
        if self.is_running:
            task = create_task(async_func())
            self.tasks.append(task)

    def start(self):
        for async_func in self.async_funcs:
            task = create_task(async_func())
            self.tasks.append(task)
        self.is_running = True

    async def wait(self):
        for task in self.tasks:
            await task
        self.is_running = False

