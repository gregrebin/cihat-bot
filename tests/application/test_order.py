from cihatbot.application.order import Empty, Status, OrderLexer
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
        lexer = OrderLexer()
        for token in lexer.tokenize(data):
            print(token.type)
            print(token.value)


