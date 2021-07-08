from mocobot.application.market import Market, Interval, Candle, TimeFrame
from mocobot.application.indicator import Indicator
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
        close = self.market["binance", "BTCBUSD", Interval(1, TimeFrame.HOUR)]["close"]
        sma = Indicator(name="sma", args={"length": 2}, min=0, max=100)
        print(sma(close))
