from cihatbot.framework.events import Event
from cihatbot.application.execution_order import ExecutionOrder
from dataclasses import dataclass


# fires app.add_session
@dataclass
class AddSessionEvent(Event):
    """
    emitted by: ui
    handled by: app
    fires: app.add_session
    """
    session_name: str


# fires app.config
@dataclass
class ConfigEvent(Event):
    """
    emitted by: ui
    handled by: app
    fires: app.config
    """
    pass


# fires session.add_trader
@dataclass
class AddTraderEvent(Event):
    """
    emitted by: ui
    handled by: session
    fires: session.add_trader
    """
    trader_name: str


# fires session.add_ui
@dataclass
class AddUiEvent(Event):
    """
    emitted by: ui
    handled by: session
    fires: session.add_ui
    """
    ui_name: str


# fires trader.add
@dataclass
class AddOrderEvent(Event):
    """
    emitted by: ui
    handled by: session
    fires: trader.add
    """
    order: ExecutionOrder
    mode: str


# fires trader.cancel
@dataclass
class CancelOrderEvent(Event):
    """
    emitted by: ui
    handled by: session
    fires: trader.cancel
    """
    order_id: str
    data_fields = {"order_id"}


# fires trader.ticker
@dataclass
class TickerEvent(Event):
    """
    emitted by: connector
    handled by: trader
    fires: trader.ticker
    """


# fires trader.clock
@dataclass
class TimerEvent(Event):
    """
    emitted by: connector
    handled by: trader
    fires: trader.timer
    """


# fires ui.submitted
@dataclass
class SubmittedEvent(Event):
    """
    emitted by: connector
    handled by: session
    fires: ui.submitted
    """
    order_id: str


# fires ui.filled
@dataclass
class FilledEvent(Event):
    """
    emitted by: connector
    handled by: session
    fires: ui.filled
    """
    order_id: str


# fires ui.rejected
@dataclass
class RejectedEvent(Event):
    """
    emitted by: connector
    handled by: session
    fires: ui.rejected
    """
    order_id: str
