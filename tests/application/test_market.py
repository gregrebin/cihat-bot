from cihatbot.application.market import Market, Trade, Interval, Candle, TimeFrame
import unittest
from pandas import DataFrame, DatetimeIndex, read_csv
import pandas_ta as ta


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
        candle1 = Candle(time=1623184833e9, open=4, close=4, high=4, low=4, volume=10)

        trade2 = Trade(price=5, quantity=20)
        interval2 = Interval(quantity=1, time_frame=TimeFrame.HOUR)
        candle2 = Candle(time=1623188433e9, open=4, close=5, high=5, low=4, volume=30)

        trade3 = Trade(price=4, quantity=3)
        interval3 = Interval(quantity=12, time_frame=TimeFrame.HOUR)
        candle3 = Candle(time=1623184833e9, open=4, close=4, high=5, low=4, volume=33)

        trade4 = Trade(price=3, quantity=7)
        interval4 = Interval(quantity=1, time_frame=TimeFrame.DAY)
        candle4 = Candle(time=1623184833e9, open=4, close=3, high=5, low=3, volume=40)

        self.market = self.market.trade("Binance", "BTCUSDT", trade1)
        self.market = self.market.candle("Binance", "BTCUSDT", interval1, candle1)
        self.market = self.market.trade("Binance", "BTCUSDT", trade2)
        self.market = self.market.candle("Binance", "BTCUSDT", interval2, candle2)
        self.market = self.market.trade("Binance", "BTCUSDT", trade3)
        self.market = self.market.candle("Binance", "BTCUSDT", interval3, candle3)
        self.market = self.market.trade("Binance", "BTCUSDT", trade4)
        self.market = self.market.candle("Binance", "BTCUSDT", interval4, candle4)

        self.assertEqual(len(self.market["Binance"]["BTCUSDT"].trades), 4)
        self.assertIn(trade1, self.market["Binance"]["BTCUSDT"].trades)
        self.assertIn(trade2, self.market["Binance"]["BTCUSDT"].trades)
        self.assertIn(trade3, self.market["Binance"]["BTCUSDT"].trades)
        self.assertIn(trade4, self.market["Binance"]["BTCUSDT"].trades)
        self.assertNotIn(Trade(), self.market["Binance"]["BTCUSDT"].trades)

        self.assertEqual(len(self.market["Binance"]["BTCUSDT"].graphs), 3)
        self.assertIn(interval1, self.market["Binance"]["BTCUSDT"].graphs)
        self.assertIn(interval2, self.market["Binance"]["BTCUSDT"].graphs)
        self.assertIn(interval3, self.market["Binance"]["BTCUSDT"].graphs)
        self.assertIn(interval4, self.market["Binance"]["BTCUSDT"].graphs)
        self.assertEqual(interval1, interval2)

        self.assertEqual(len(self.market["Binance"]["BTCUSDT"][interval1].candles), 2)
        self.assertEqual(len(self.market["Binance"]["BTCUSDT"][interval3].candles), 1)
        self.assertEqual(len(self.market["Binance"]["BTCUSDT"][interval4].candles), 1)

        self.assertIn(candle1, self.market["Binance"]["BTCUSDT"][interval1].candles)
        self.assertIn(candle2, self.market["Binance"]["BTCUSDT"][interval1].candles)
        self.assertIn(candle3, self.market["Binance"]["BTCUSDT"][interval3].candles)
        self.assertIn(candle4, self.market["Binance"]["BTCUSDT"][interval4].candles)

        print(self.market["Binance"]["BTCUSDT"][interval1].dataframe)

    def test_pandas_ta(self):

        df = DataFrame()
        df = read_csv("pandas_ta_datas_short.csv", sep=",")
        df.set_index(DatetimeIndex(df["date"]), inplace=True, drop=True)
        print(df)

        # df.ta.log_return(append=True)
        df.ta.macd(append=True)
        # df.ta.sma(append=True)
        # print(df.head(15))

        df.ta.strategy()
        print(df)

