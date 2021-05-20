from cihatbot.framework.events import Event


# fires app.add_user
class AddUserEvent(Event):
    """
    emitted by: ui
    handled by: app
    fires: app.add_user
    """
    name = "NEW_USER"
    data_fields = {"user"}


# fires app.config
class ConfigEvent(Event):
    """
    emitted by: ui
    handled by: app
    fires: app.config
    """
    name = "CONFIG"


# fires user.add_trader
class AddTraderEvent(Event):
    """
    emitted by: ui
    handled by: user
    fires: user.add_trader
    """
    name = "ADD_TRADER"
    data_fields = {"trader"}


# fires user.add_ui
class AddUiEvent(Event):
    """
    emitted by: ui
    handled by: user
    fires: user.add_ui
    """
    name = "ADD_UI"
    data_fields = {"ui"}


# fires trader.add
class AddOrderEvent(Event):
    """
    emitted by: ui
    handled by: user
    fires: trader.add
    """
    name = "ADD"
    data_fields = {"order", "mode"}


# fires trader.cancel
class CancelOrderEvent(Event):
    """
    emitted by: ui
    handled by: user
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
    handled by: user
    fires: ui.submitted
    """
    name = "SUBMITTED"
    data_fields = {"all", "single"}


# fires ui.filled
class FilledEvent(Event):
    """
    emitted by: connector
    handled by: user
    fires: ui.filled
    """
    name = "FILLED"
    data_fields = {"all", "single"}


# fires ui.rejected
class RejectedEvent(Event):
    """
    emitted by: connector
    handled by: user
    fires: ui.rejected
    """
    name = "ERROR"
    data_fields = {"order", "message"}
