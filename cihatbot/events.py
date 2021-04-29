from __future__ import annotations
from asyncio import Queue
from typing import Dict, Any, Set, List, Callable, Type


class Event:
    name: str = "EVENT"
    data_fields: Set[str] = {}

    def __init__(self, data: Dict[str, Any]):
        for field in self.data_fields:
            if field not in data:
                raise DataException()
        self.data: Dict[str, Any] = data

    def __str__(self):
        return f"""{self.name} - {self.data}"""

    def is_type(self, event_type: Type[Event]):
        return self.name == event_type.name


class StopEvent(Event):
    name = "STOP"


class DataException(Exception):
    pass


class EventListener:

    def __init__(self):
        self.queue: Queue = Queue()

    async def listen(self, on_event: Callable[[Event], None]):
        stop = False
        while not stop:
            event = await self.queue.get()
            on_event(event)
            stop = event.is_type(StopEvent)

    async def stop(self):
        await self.queue.put(StopEvent({}))


class EventEmitter:

    def __init__(self):
        self.listeners_queues: List[Queue] = []

    def add_listener(self, listener: EventListener):
        self.listeners_queues.append(listener.queue)

    def emit(self, event: Event):
        for listener_queue in self.listeners_queues:
            listener_queue.put_nowait(event)
