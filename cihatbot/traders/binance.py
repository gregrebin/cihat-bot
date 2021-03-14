from cihatbot.events import Event
from cihatbot.modules.trader import Trader
from binance.client import Client


class Binance(Trader):

    def __init__(self, config):
        super().__init__(config)
        self.client = Client(api_key=config["api"], api_secret=config["secret"])

    def run(self):
        print(self.client.get_system_status())

    def connect(self, event: Event):
        print("Connecting")
        print("User", event.data["user"])
        print("Password", event.data["password"])
        # self.client = Client(api_key=event.data["user"], api_secret=event.data["password"])

    def execute(self, event: Event):
        print("Executing order: ", event.data["order"])

    # def buy(self, data: Dict[str, str]):
    #     order = self.client.create_test_order(
    #         symbol=data["symbol"],
    #         side=self.client.SIDE_BUY,
    #         type=self.client.ORDER_TYPE_MARKET,
    #         quantity=float(data["quantity"])
    #     )
    #     print(order)
    #
    # def sell(self, data: Dict[str, str]):
    #     order = self.client.create_test_order(
    #         symbol=data["symbol"],
    #         side=self.client.SIDE_SELL,
    #         type=self.client.ORDER_TYPE_MARKET,
    #         quantity=float(data["quantity"])
    #     )
    #     print(order)

