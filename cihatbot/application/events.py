from cihatbot.framework.events import Event


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