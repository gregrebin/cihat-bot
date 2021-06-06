from __future__ import annotations
from asyncio import Queue
from typing import Dict, Any, Set, List, Callable, Type
from dataclasses import dataclass


@dataclass
class Event:
    pass


@dataclass
class StopEvent(Event):
    pass


class EventListener:

    def __init__(self):
        self.queue: Queue = Queue()

    async def listen(self, on_event: Callable[[Event], None]):
        stop = False
        while not stop:
            event = await self.queue.get()
            on_event(event)
            stop = isinstance(event, StopEvent)

    async def stop(self):
        await self.queue.put(StopEvent())


class EventEmitter:

    def __init__(self):
        self.listeners_queues: List[Queue] = []

    def add_listener(self, listener: EventListener):
        self.listeners_queues.append(listener.queue)

    def emit(self, event: Event):
        for listener_queue in self.listeners_queues:
            listener_queue.put_nowait(event)
