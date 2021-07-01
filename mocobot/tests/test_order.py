from mocobot.application.order import Order, Empty, Status, OrderLexer, OrderParser, Mode, Command
import unittest


class TestOrder(unittest.TestCase):

    def setUp(self) -> None:
        self.order = Empty()

    def test_empty(self):
        self.order = Empty()
        self.assertEqual(self.order.status, Status.NEW)
        print(self.order.uid)

    def test_lexer(self):
        data = "buy 0.5 BTCUSDT, 1 ETH in Binance at 55000"
        data = "[parallel buy 5 BTCUSDT in Binance at 30000, buy ETHUSDT in Coinbase at 2000 for 1000]"
        lexer = OrderLexer()
        for token in lexer.tokenize(data):
            print(f"""{token.type}: {token.value} with type {type(token.value)}""")

    def test_parser(self):
        data = "empty"
        data = "buy 5 BTCUSDT in Binance at 20000"
        data = "buy BTCUSDT in Binance at 20000 for 1000"
        data = "[parallel buy 5 BTCUSDT in Binance at 20000, buy 5 BTCUSDT in Binance at 20000]"
        data = "[parallel buy 5 BTCUSDT in Binance at 20000, [sequent buy 5 BTCUSDT in Binance at 30000, buy ETHUSDT in Coinbase at 2000 for 1000], buy 5 BTCUSDT in Binance at 20000]"
        data = "[parallel buy 5 BTCUSDT in Binance at 20000, buy 5 BTCUSDT in Binance at 20000, [sequent buy 5 BTCUSDT in Binance at 30000, buy ETHUSDT in Coinbase at 2000 for 1000]]"
        data = "[parallel buy 5 BTCUSDT in Binance at 20000, [sequent [parallel buy 5 BTCUSDT in Binance at 30000, buy ETHUSDT in Coinbase at 2000 for 1000], buy ETHUSDT in Coinbase at 2000 for 1000], buy 5 BTCUSDT in Binance at 20000]"
        result = Order.parse(data)
        print(result)



