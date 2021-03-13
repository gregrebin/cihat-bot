from cihatbot.trader import Trader
from binance.client import Client
from typing import Dict


class Binance(Trader):

    def __init__(self, config):
        super().__init__(config)
        self.client = Client(api_key=config["api"], api_secret=config["secret"])

    def run(self):
        print(self.client.ping())

    def buy(self, data: Dict[str, str]):
        order = self.client.create_test_order(
            symbol="BTCBUSD",
            side=self.client.SIDE_BUY,
            type=self.client.ORDER_TYPE_MARKET,
            quantity=0.0002
        )
        print(order)

    def sell(self, data: Dict[str, str]):
        order = self.client.create_test_order(
            symbol="BTCBUSD",
            side=self.client.SIDE_SELL,
            type=self.client.ORDER_TYPE_MARKET,
            quantity=0.0002
        )
        print(order)

