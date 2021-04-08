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


class ConnectEvent(Event):
    name = "CONNECT"
    data_fields = {"user", "password"}


class AddEvent(Event):
    name = "ADD"
    data_fields = {"order", "mode"}


class DeleteEvent(Event):
    name = "DELETE"
    data_fields = {"order_id"}


class ConnectedEvent(Event):
    name = "CONNECTED"
    data_fields = {"user"}


class AddedEvent(Event):
    name = "ADDED"
    data_fields = {"all", "single"}


class DeletedEvent(Event):
    name = "DELETED"
    data_fields = {"all", "order_id"}


class SubmittedEvent(Event):
    name = "SUBMITTED"
    data_fields = {"all", "single"}


class FilledEvent(Event):
    name = "FILLED"
    data_fields = {"all", "single"}


class CancelledEvent(Event):
    name = "CANCELLED"
    data_fields = {"all", "single"}


class ErrorEvent(Event):
    name = "ERROR"
    data_fields = {"order", "message"}


class UserEvent(Event):
    name = "USER"
    data_fields = {"external_id", "status"}


class TickerEvent(Event):
    name = "TICKER"


class TimerEvent(Event):
    name = "TIMER"


class AddTraderEvent(Event):
    name = "ADD_TRADER"
    data_fields = {"trader_name", "connector_name", "config"}


class AddUiEvent(Event):
    name = "ADD_UI"
    data_fields = {"ui_name", "parser_name", "config"}


class AddUserEvent(Event):
    name = "NEW_USER"
    data_fields = {"ui", "parser", "trader", "connector"}


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
            listener_queue.put(event)
