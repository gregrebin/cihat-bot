from cihatbot.utils.execution_order import SingleExecutionOrder, ExecutionParams, ExecutionConditions
from cihatbot.utils.parser import CompleteParser
import time


class ExecutionOrderTest:

    def __init__(self):
        string = "[p " \
                 "buy ATOMBUSD 20.0 10.0, " \
                 "[s [p buy ADABUSD 0.9 10.0, buy ADABUSD 1.0 10.0, buy ADABUSD 1.2 10.0], sell ADABUSD 1.5 30.0], " \
                 "[s [p buy ETHBUSD 1700.0 0.5, buy ETHBUSD 1500.0 0.5], sell ETHBUSD 2000.0 1.0], " \
                 "buy DOTBUSD 35.0 10.0]"
        self.order = CompleteParser().parse(string)
        print("Initialized order:", self.order)

    def test_execute(self):
        def execute_func(order: SingleExecutionOrder):
            print("Executing single order", order)
            return True
        self.order.execute(execute_func)
        print("Order after execution:", self.order)

    def test_add(self):
        to_add_par = SingleExecutionOrder(
            ExecutionParams("buy", "BTCBUSD", 60000.0, 1),
            ExecutionConditions(time.time())
        )
        to_add_seq = SingleExecutionOrder(
            ExecutionParams("sell", "BTCBUSD", 80000.0, 1),
            ExecutionConditions(time.time())
        )
        self.order = self.order.add_parallel(to_add_par)
        self.order = self.order.add_sequential(to_add_seq)
        print("Order after add:", self.order)

    def test_delete(self):
        to_remove = self.order.orders[1].orders[0].orders[2]
        self.order.remove(to_remove)
        print("Order after remove:", self.order)


if __name__ == '__main__':
    test = ExecutionOrderTest()
    test.test_execute()
    test.test_execute()
    test.test_execute()
    test.test_delete()
    test.test_add()

