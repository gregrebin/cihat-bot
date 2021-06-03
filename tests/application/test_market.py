from cihatbot.application.market import Market, Trade, Interval, Candle, TimeFrame
import unittest


class TestMarket(unittest.TestCase):

    def setUp(self) -> None:
        self.market = Market()

    def test_empty(self):
        self.assertEqual(len(self.market.exchanges), 0)

    def test_new_exchange(self):

        trade = Trade()
        interval = Interval()
        candle = Candle()

        self.market = self.market.update("Binance", "BTCUSDT", trade, interval, candle)
        self.market = self.market.update("Kraken", "BTCUSDT", trade, interval, candle)
        self.market = self.market.update("Gate.io", "BTCUSDT", trade, interval, candle)

        self.assertEqual(len(self.market.exchanges), 3)
        self.assertEqual(self.market.exchanges[0].name, "Binance")
        self.assertEqual(self.market.exchanges[1].name, "Kraken")
        self.assertEqual(self.market.exchanges[2].name, "Gate.io")

    def test_new_pair(self):

        trade = Trade()
        interval = Interval()
        candle = Candle()

        self.market = self.market.update("Binance", "BTCUSDT", trade, interval, candle)
        self.market = self.market.update("Binance", "BTCBUSD", trade, interval, candle)
        self.market = self.market.update("Binance", "ETHBTC", trade, interval, candle)

        self.assertEqual(len(self.market.exchanges[0].pairs), 3)
        self.assertEqual(self.market.exchanges[0].pairs[0], "BTCUSDT")
        self.assertEqual(self.market.exchanges[0].pairs[1], "BTCBUSD")
        self.assertEqual(self.market.exchanges[0].pairs[2], "ETHBTC")

    def test_new_trade(self):

        trade1 = Trade(price=4, quantity=10)
        interval1 = Interval(quantity=1, time_frame=TimeFrame.HOUR)
        candle1 = Candle(open=4, close=4, height=4, low=4, volume=10)

        trade2 = Trade(price=5, quantity=20)
        interval2 = Interval(quantity=1, time_frame=TimeFrame.HOUR)
        candle2 = Candle(open=4, close=5, height=5, low=4, volume=30)

        trade3 = Trade(price=4, quantity=3)
        interval3 = Interval(quantity=12, time_frame=TimeFrame.HOUR)
        candle3 = Candle(open=4, close=4, height=5, low=4, volume=33)

        trade4 = Trade(price=3, quantity=7)
        interval4 = Interval(quantity=1, time_frame=TimeFrame.DAY)
        candle4 = Candle(open=4, close=3, height=5, low=3, volume=40)

        self.market = self.market.update("Binance", "BTCUSDT", trade1, interval1, candle1)
        self.market = self.market.update("Binance", "BTCUSDT", trade2, interval2, candle2)
        self.market = self.market.update("Binance", "BTCUSDT", trade3, interval3, candle3)
        self.market = self.market.update("Binance", "BTCUSDT", trade4, interval4, candle4)

        self.assertEqual(len(self.market.exchanges[0].pairs[0].trades), 4)
        self.assertIn(trade1, self.market.exchanges[0].pairs[0].trades)
        self.assertIn(trade2, self.market.exchanges[0].pairs[0].trades)
        self.assertIn(trade3, self.market.exchanges[0].pairs[0].trades)
        self.assertIn(trade4, self.market.exchanges[0].pairs[0].trades)
        self.assertNotIn(Trade(), self.market.exchanges[0].pairs[0].trades)

        self.assertEqual(len(self.market.exchanges[0].pairs[0].candles), 3)
        self.assertIn(interval1, self.market.exchanges[0].pairs[0].candles)
        self.assertIn(interval2, self.market.exchanges[0].pairs[0].candles)
        self.assertIn(interval3, self.market.exchanges[0].pairs[0].candles)
        self.assertIn(interval4, self.market.exchanges[0].pairs[0].candles)
        self.assertEqual(interval1, interval2)

        self.assertEqual(len(self.market.exchanges[0].pairs[0].candles[interval1]), 2)
        self.assertEqual(len(self.market.exchanges[0].pairs[0].candles[interval3]), 1)
        self.assertEqual(len(self.market.exchanges[0].pairs[0].candles[interval4]), 1)

        self.assertIn(candle1, self.market.exchanges[0].pairs[0].candles[interval1])
        self.assertIn(candle2, self.market.exchanges[0].pairs[0].candles[interval1])
        self.assertIn(candle3, self.market.exchanges[0].pairs[0].candles[interval3])
        self.assertIn(candle4, self.market.exchanges[0].pairs[0].candles[interval4])


