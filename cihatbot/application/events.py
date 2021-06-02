from cihatbot.framework.events import Event
from cihatbot.application.order import Order, Mode
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
    order: Order
    mode: Mode


# fires trader.cancel
@dataclass
class CancelOrderEvent(Event):
    """
    emitted by: ui
    handled by: session
    fires: trader.cancel
    """
    uid: str
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
    uid: str


# fires ui.filled
@dataclass
class FilledEvent(Event):
    """
    emitted by: connector
    handled by: session
    fires: ui.filled
    """
    uid: str


# fires ui.rejected
@dataclass
class RejectedEvent(Event):
    """
    emitted by: connector
    handled by: session
    fires: ui.rejected
    """
    uid: str
