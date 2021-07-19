from mocobot.application.market import Market, Interval, Candle, TimeFrame
from mocobot.application.indicator import Indicator
from dataclasses import replace
import unittest


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
        self.market = self.market.add_candle("binance", "BTCUSDT", Interval(1, TimeFrame.HOUR), candle1)

        df = self.market["binance", "BTCBUSD", Interval(1, TimeFrame.HOUR)]
        sma = Indicator(name="sma", settings={"length": 2}, min=0, max=100)
        self.assertTrue(sma.check(df))

        for i in range(50):
            candle3 = replace(candle3, time=candle3.time + 3600)
            self.market = self.market.add_candle("binance", "BTCBUSD", Interval(1, TimeFrame.HOUR), candle3)

        df = self.market["binance", "BTCBUSD", Interval(1, TimeFrame.HOUR)]
        macd = Indicator(name="macd", settings={"fast": 8, "slow": 21}, min=-1, max=100, line="macd")
        self.assertTrue(macd.check(df))

        macd = Indicator(name="macd", settings={"fast": 8, "slow": 21}, min=1, max=100, line="macd")
        self.assertFalse(macd.check(df))

        price = Indicator(name="price", min=20, max=90)
        self.assertFalse(price.check(df))

