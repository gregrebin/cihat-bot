from cihatbot.execution_order.execution_order import SingleExecutionOrder, ExecutionConditions, ExecutionParams


class Connector:

    ORDER_DELAY: float = 0.0
    QUERY_DELAY: float = 0.0

    def connect(self, key: str, secret: str) -> None:
        pass

    def satisfied(self, execution_order: SingleExecutionOrder) -> bool:
        pass

    def submit(self, execution_order: SingleExecutionOrder) -> int:
        pass

    def is_filled(self, execution_order: SingleExecutionOrder) -> bool:
        pass

    def cancel(self, execution_order: SingleExecutionOrder) -> None:
        pass


class ConnectorException(Exception):
    def __init__(self, message: str, order: SingleExecutionOrder):
        self.message = message
        self.order = order
