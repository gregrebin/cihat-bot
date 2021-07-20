import typing
import re
from mocobot.application.order import Order, Empty, Status, OrderLexer, OrderParser, Mode, Command, Multiple
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
        data = "[parallel buy 5 BTCUSDT in Binance at 30000; buy ETHUSDT in Coinbase at 2000 for 1000]"
        lexer = OrderLexer()
        for token in lexer.tokenize(data):
            print(f"""{token.type}: {token.value} with type {type(token.value)}""")

    def test_parser(self):
        data = "empty"
        data = "buy 5 BTCUSDT in Binance at 20000"
        data = "buy BTCUSDT in Binance at 20000 for 1000"
        data = "[parallel buy 5 BTCUSDT in Binance at 20000; buy 5 BTCUSDT in Binance at 20000]"
        data = "[parallel buy 5 BTCUSDT in Binance at 20000; [sequent buy 5 BTCUSDT in Binance at 30000; buy ETHUSDT in Coinbase at 2000 for 1000]; buy 5 BTCUSDT in Binance at 20000]"
        data = "[parallel buy 5 BTCUSDT in Binance at 20000; buy 5 BTCUSDT in Binance at 20000; [sequent buy 5 BTCUSDT in Binance at 30000; buy ETHUSDT in Coinbase at 2000 for 1000]]"
        data = "[parallel buy 5 BTCUSDT in Binance at 20000; [sequent [parallel buy 5 BTCUSDT in Binance at 30000; buy ETHUSDT in Coinbase at 2000 for 1000]; buy ETHUSDT in Coinbase at 2000 for 1000]; buy 5 BTCUSDT in Binance at 20000]"
        data = "buy 5 BTCUSDT in Binance at 20000 if macd@31m = 5"
        data = "buy 5 BTCUSDT in Binance at 20000 if macd(4h, histogram, fast:8, slow:1) = 1/2 and sma(30m) = 5 and price = 10/100"
        data = "buy 5 BTCUSDT in Binance at 20000 if macd@4h(fast:8,slow:1)histogram=1/2 and sma@30m=5 and price=10/100"
        # lexer = OrderLexer()
        # for token in lexer.tokenize(data):
        #     print(f"""{token.type}: {token.value} with type {type(token.value)}""")
        result = Order.parse(data)
        print(result)

    def test_order(self):

        # Creating orders
        self.order = self.order.add(Order.parse("buy 5 BTCUSDT in Binance at 20000"), Mode.PARALLEL)
        self.order = self.order.add(Order.parse("buy 10 BTCUSDT in Binance at 30000"), Mode.PARALLEL)
        self.order = self.order.add(Order.parse("buy 3 BTCUSDT in Binance at 40000"), Mode.PARALLEL)
        self.order = self.order.add(Order.parse("[parallel buy 5 BTCUSDT in Binance at 20000; buy 5 BTCUSDT in Binance at 20000]"), Mode.SEQUENT)

        o1 = self.order.orders[0].orders[0].uid
        o2 = self.order.orders[0].orders[1].uid
        o3 = self.order.orders[0].orders[2].uid
        o4 = self.order.orders[1].orders[0].uid
        o5 = self.order.orders[1].orders[1].uid

        # Cancelling
        self.order = self.order.cancel(o2)
        self.assertEqual(self.order.orders[0].orders[1].status, Status.CANCELLED)

        gen = self.order.get()
        self.assertEqual(next(gen).uid, o1)
        self.assertEqual(next(gen).uid, o3)
        self.assertRaises(StopIteration, lambda: next(gen))

        gen = self.order.get(False)
        self.assertEqual(next(gen).uid, o1)
        self.assertEqual(next(gen).uid, o2)
        self.assertEqual(next(gen).uid, o3)
        self.assertEqual(next(gen).uid, o4)
        self.assertEqual(next(gen).uid, o5)

        # Submitting
        self.order = self.order.update_status(uid=o1, status=Status.SUBMITTED)
        self.order = self.order.update_status(uid=o3, status=Status.FILLED)

        self.assertEqual(self.order.orders[0].orders[0].status, Status.SUBMITTED)
        self.assertEqual(self.order.orders[0].orders[2].status, Status.FILLED)

        gen = self.order.get()
        self.assertEqual(next(gen).uid, o1)
        self.assertRaises(StopIteration, lambda: next(gen))

        # Set eid
        self.order = self.order.set_eid(o1, "1122334455")
        self.assertEqual(self.order.orders[0].orders[0].eid, "1122334455")

        # Cancel submitted
        self.order = self.order.cancel(o1)
        gen = self.order.get()
        order = next(gen)
        self.assertEqual(order.status, Status.SUBMITTED)
        self.assertTrue(order.to_cancel)
        self.assertRaises(StopIteration, lambda: next(gen))

        # Order cancelled
        self.order = self.order.update_status(eid="1122334455", status=Status.CANCELLED)
        gen = self.order.get()
        self.assertEqual(next(gen).uid, o4)
        self.assertEqual(next(gen).uid, o5)
        self.assertRaises(StopIteration, lambda: next(gen))

        # Rejected
        self.order = self.order.update_status(uid=o5, status=Status.REJECTED)
        gen = self.order.get()
        self.assertEqual(next(gen).uid, o4)
        self.assertRaises(StopIteration, lambda: next(gen))





