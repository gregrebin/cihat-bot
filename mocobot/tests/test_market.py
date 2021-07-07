from mocobot.application.market import Market, Interval, Candle, TimeFrame, Indicator
import unittest
from dataclasses import replace
from pandas import DataFrame, DatetimeIndex, read_csv
import pandas_ta as ta


class TestMarket(unittest.TestCase):

    def setUp(self) -> None:
        self.market = Market()

    def test_candle(self):
        candle1 = Candle(time=1625641200, open=10, high=15, low=8, close=13, volume=100)
        candle2 = Candle(time=1625644800, open=13, high=23, low=13, close=18, volume=120)
        candle3 = Candle(time=1625648400, open=18, high=25, low=10, close=15, volume=90)
        self.market = self.market.add_candle("binance", "BTCBUSD", Interval(1, TimeFrame.HOUR), candle1)
        self.market = self.market.add_candle("binance", "BTCBUSD", Interval(1, TimeFrame.HOUR), candle2)
        self.market = self.market.add_candle("binance", "BTCBUSD", Interval(1, TimeFrame.HOUR), candle3)
        print(self.market.charts[0].candles)

    # def test_empty(self):
    #     self.assertEqual(len(self.market.exchanges), 0)
    #
    # def test_new_exchange(self):
    #
    #     trade = Trade()
    #     interval = Interval()
    #     candle = Candle()
    #
    #     self.market = self.market.update("Binance", "BTCUSDT", trade, interval, candle)
    #     self.market = self.market.update("Kraken", "BTCUSDT", trade, interval, candle)
    #     self.market = self.market.update("Gate.io", "BTCUSDT", trade, interval, candle)
    #
    #     self.assertEqual(len(self.market.exchanges), 3)
    #     self.assertEqual(self.market.exchanges[0].name, "Binance")
    #     self.assertEqual(self.market.exchanges[1].name, "Kraken")
    #     self.assertEqual(self.market.exchanges[2].name, "Gate.io")
    #
    # def test_new_pair(self):
    #
    #     trade = Trade()
    #     interval = Interval()
    #     candle = Candle()
    #
    #     self.market = self.market.update("Binance", "BTCUSDT", trade, interval, candle)
    #     self.market = self.market.update("Binance", "BTCBUSD", trade, interval, candle)
    #     self.market = self.market.update("Binance", "ETHBTC", trade, interval, candle)
    #
    #     self.assertEqual(len(self.market.exchanges[0].pairs), 3)
    #     self.assertEqual(self.market.exchanges[0].pairs[0], "BTCUSDT")
    #     self.assertEqual(self.market.exchanges[0].pairs[1], "BTCBUSD")
    #     self.assertEqual(self.market.exchanges[0].pairs[2], "ETHBTC")
    #
    # def test_new_trade(self):
    #
    #     trade1 = Trade(price=4, quantity=10)
    #     interval1 = Interval(quantity=1, time_frame=TimeFrame.HOUR)
    #     candle1 = Candle(time=1623184833e9, open=4, close=4, high=4, low=4, volume=10)
    #
    #     trade2 = Trade(price=5, quantity=20)
    #     interval2 = Interval(quantity=1, time_frame=TimeFrame.HOUR)
    #     candle2 = Candle(time=1623184933e9, open=4, close=5, high=5, low=4, volume=30)
    #
    #     trade3 = Trade(price=4, quantity=3)
    #     interval3 = Interval(quantity=12, time_frame=TimeFrame.HOUR)
    #     candle3 = Candle(time=1623184833e9, open=4, close=4, high=5, low=4, volume=33)
    #
    #     trade4 = Trade(price=3, quantity=7)
    #     interval4 = Interval(quantity=1, time_frame=TimeFrame.DAY)
    #     candle4 = Candle(time=1623184833e9, open=4, close=3, high=5, low=3, volume=40)
    #
    #     self.market = self.market.trade("Binance", "BTCUSDT", trade1)
    #     self.market = self.market.candle("Binance", "BTCUSDT", interval1, candle1)
    #     self.market = self.market.trade("Binance", "BTCUSDT", trade2)
    #     self.market = self.market.candle("Binance", "BTCUSDT", interval2, candle2)
    #     self.market = self.market.trade("Binance", "BTCUSDT", trade3)
    #     self.market = self.market.candle("Binance", "BTCUSDT", interval3, candle3)
    #     self.market = self.market.trade("Binance", "BTCUSDT", trade4)
    #     self.market = self.market.candle("Binance", "BTCUSDT", interval4, candle4)
    #
    #     sma = Indicator("sma", (("length", 2),))
    #     self.market = self.market.indicator("Binance", "BTCUSDT", interval1, sma)
    #
    #     self.assertEqual(len(self.market["Binance"]["BTCUSDT"].trades), 4)
    #     self.assertIn(trade1, self.market["Binance"]["BTCUSDT"].trades)
    #     self.assertIn(trade2, self.market["Binance"]["BTCUSDT"].trades)
    #     self.assertIn(trade3, self.market["Binance"]["BTCUSDT"].trades)
    #     self.assertIn(trade4, self.market["Binance"]["BTCUSDT"].trades)
    #     self.assertNotIn(Trade(), self.market["Binance"]["BTCUSDT"].trades)
    #
    #     self.assertEqual(len(self.market["Binance"]["BTCUSDT"].charts), 3)
    #     self.assertIn(interval1, self.market["Binance"]["BTCUSDT"].charts)
    #     self.assertIn(interval2, self.market["Binance"]["BTCUSDT"].charts)
    #     self.assertIn(interval3, self.market["Binance"]["BTCUSDT"].charts)
    #     self.assertIn(interval4, self.market["Binance"]["BTCUSDT"].charts)
    #     self.assertEqual(interval1, interval2)
    #
    #     self.assertEqual(len(self.market["Binance"]["BTCUSDT"][interval1].candles), 2)
    #     self.assertEqual(len(self.market["Binance"]["BTCUSDT"][interval3].candles), 1)
    #     self.assertEqual(len(self.market["Binance"]["BTCUSDT"][interval4].candles), 1)
    #
    #     self.assertIn(candle1, self.market["Binance"]["BTCUSDT"][interval1].candles)
    #     self.assertIn(candle2, self.market["Binance"]["BTCUSDT"][interval1].candles)
    #     self.assertIn(candle3, self.market["Binance"]["BTCUSDT"][interval3].candles)
    #     self.assertIn(candle4, self.market["Binance"]["BTCUSDT"][interval4].candles)
    #
    #     print(self.market["Binance"]["BTCUSDT"][interval1].dataframe)
    #
    #     for i in range(20):
    #         candle2 = replace(candle2, time=(candle2.time+100e9))
    #         self.market = self.market.candle("Binance", "BTCUSDT", interval1, candle2)
    #
    #     macd = Indicator("macd", (("fast", 8), ("slow", 41)))
    #     self.market = self.market.indicator("Binance", "BTCUSDT", interval1, macd)
    #     macd = Indicator("macd", (("fast", 8), ("slow", 21)))
    #     self.market = self.market.indicator("Binance", "BTCUSDT", interval1, macd)
    #
    #     print(self.market["Binance"]["BTCUSDT"][interval1].dataframe)
    #     print(self.market["Binance"]["BTCUSDT"][interval1].indicators)
    #     print(self.market["Binance"]["BTCUSDT"][interval1].pending)
    #
    #     for i in range(20):
    #         candle2 = replace(candle2, time=(candle2.time+100e9))
    #         self.market = self.market.candle("Binance", "BTCUSDT", interval1, candle2)
    #
    #     print(self.market["Binance"]["BTCUSDT"][interval1].dataframe)
    #     print(self.market["Binance"]["BTCUSDT"][interval1].indicators)
    #     print(self.market["Binance"]["BTCUSDT"][interval1].pending)
    #
    #     for i in range(20):
    #         candle2 = replace(candle2, time=(candle2.time+100e9))
    #         self.market = self.market.candle("Binance", "BTCUSDT", interval1, candle2)
    #
    #     print(self.market["Binance"]["BTCUSDT"][interval1].dataframe)
    #     print(self.market["Binance"]["BTCUSDT"][interval1].indicators)
    #     print(self.market["Binance"]["BTCUSDT"][interval1].pending)
    #
    # def test_pandas_ta(self):
    #
    #     df = DataFrame()
    #     df = read_csv("pandas_ta_datas_short.csv", sep=",")
    #     df.set_index(DatetimeIndex(df["date"]), inplace=True, drop=True)
    #     print(df)
    #
    #     # df.ta.log_return(append=True)
    #     df.ta.macd(append=True)
    #     # df.ta.sma(append=True)
    #     # print(df.head(15))
    #
    #     df.ta.strategy()
    #     print(df)

