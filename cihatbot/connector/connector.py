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


class RejectedOrder(Exception):
    def __init__(self, order: SingleExecutionOrder):
        self.order = order


class NonExistentOrder(Exception):
    def __init__(self, order: SingleExecutionOrder):
        self.order = order
