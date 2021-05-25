from cihatbot.framework.events import Event


# fires app.add_session
class AddSessionEvent(Event):
    """
    emitted by: ui
    handled by: app
    fires: app.add_session
    """
    name = "NEW_SESSION"
    data_fields = {"session"}


# fires app.config
class ConfigEvent(Event):
    """
    emitted by: ui
    handled by: app
    fires: app.config
    """
    name = "CONFIG"


# fires session.add_trader
class AddTraderEvent(Event):
    """
    emitted by: ui
    handled by: session
    fires: session.add_trader
    """
    name = "ADD_TRADER"
    data_fields = {"trader"}


# fires session.add_ui
class AddUiEvent(Event):
    """
    emitted by: ui
    handled by: session
    fires: session.add_ui
    """
    name = "ADD_UI"
    data_fields = {"ui"}


# fires trader.add
class AddOrderEvent(Event):
    """
    emitted by: ui
    handled by: session
    fires: trader.add
    """
    name = "ADD"
    data_fields = {"order", "mode"}


# fires trader.cancel
class CancelOrderEvent(Event):
    """
    emitted by: ui
    handled by: session
    fires: trader.cancel
    """
    name = "CANCEL"
    data_fields = {"order_id"}


# fires trader.ticker
class TickerEvent(Event):
    """
    emitted by: connector
    handled by: trader
    fires: trader.ticker
    """
    name = "TICKER"


# fires trader.clock
class TimerEvent(Event):
    """
    emitted by: connector
    handled by: trader
    fires: trader.timer
    """
    name = "TIMER"


# fires ui.submitted
class SubmittedEvent(Event):
    """
    emitted by: connector
    handled by: session
    fires: ui.submitted
    """
    name = "SUBMITTED"
    data_fields = {"all", "single"}


# fires ui.filled
class FilledEvent(Event):
    """
    emitted by: connector
    handled by: session
    fires: ui.filled
    """
    name = "FILLED"
    data_fields = {"all", "single"}


# fires ui.rejected
class RejectedEvent(Event):
    """
    emitted by: connector
    handled by: session
    fires: ui.rejected
    """
    name = "ERROR"
    data_fields = {"order", "message"}
