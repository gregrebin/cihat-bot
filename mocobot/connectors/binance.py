from mocobot.application.connector import Connector, CandleEvent, UserEvent
from mocobot.application.order import Single, Command, Status
from mocobot.application.market import Interval, TimeFrame, Candle
from binance import Client, ThreadedWebsocketManager
from binance.enums import *
from bidict import bidict
from typing import Tuple, Type, Set
from configparser import SectionProxy


class BinanceConnector(Connector):

    EXCHANGE = "binance"

    INTERVALS = bidict({
        Interval(1, TimeFrame.MINUTE): KLINE_INTERVAL_1MINUTE,
        Interval(3, TimeFrame.MINUTE): KLINE_INTERVAL_3MINUTE,
        Interval(5, TimeFrame.MINUTE): KLINE_INTERVAL_5MINUTE,
        Interval(15, TimeFrame.MINUTE): KLINE_INTERVAL_15MINUTE,
        Interval(30, TimeFrame.MINUTE): KLINE_INTERVAL_30MINUTE,
        Interval(1, TimeFrame.HOUR): KLINE_INTERVAL_1HOUR,
        Interval(2, TimeFrame.HOUR): KLINE_INTERVAL_2HOUR,
        Interval(4, TimeFrame.HOUR): KLINE_INTERVAL_4HOUR,
        Interval(6, TimeFrame.HOUR): KLINE_INTERVAL_6HOUR,
        Interval(8, TimeFrame.HOUR): KLINE_INTERVAL_8HOUR,
        Interval(12, TimeFrame.HOUR): KLINE_INTERVAL_12HOUR,
        Interval(1, TimeFrame.DAY): KLINE_INTERVAL_1DAY,
        Interval(3, TimeFrame.DAY): KLINE_INTERVAL_3DAY,
        Interval(1, TimeFrame.WEEK): KLINE_INTERVAL_1WEEK,
        Interval(1, TimeFrame.MONTH): KLINE_INTERVAL_1MONTH,
    })
    STATUS = {
        ORDER_STATUS_NEW: Status.SUBMITTED,
        ORDER_STATUS_PARTIALLY_FILLED: Status.SUBMITTED,
        ORDER_STATUS_FILLED: Status.FILLED,
        ORDER_STATUS_CANCELED: Status.CANCELLED,
        ORDER_STATUS_REJECTED: Status.REJECTED,
        ORDER_STATUS_EXPIRED: Status.REJECTED,
    }

    # def __init__(self, config: SectionProxy, category: Type, name: str, username: str, password: str):
    #     super().__init__(config, category, name, username, password)
    #     self.client: Client = Client(username, password)
    #     self.socket_manager: ThreadedWebsocketManager = ThreadedWebsocketManager(username, password)
    #     self.open_sockets: Set[Tuple[str, Interval]] = set()

    def post_init(self) -> None:
        self.client: Client = Client(self.username, self.password)
        self.socket_manager: ThreadedWebsocketManager = ThreadedWebsocketManager(self.username, self.password)
        self.open_sockets: Set[Tuple[str, Interval]] = set()

    @property
    def exchange(self) -> str:
        return self.EXCHANGE

    def pre_run(self) -> None:
        self.socket_manager.start()

    async def on_run(self) -> None:
        self.socket_manager.start_user_socket(self._user_handler)
        # self.start_candles("BTCUSDT", Interval(1, TimeFrame.MINUTE))

    def _user_handler(self, msg: dict):
        event_type = msg["e"]
        if not event_type == "executionReport": return
        msg_status = msg["X"]
        if msg_status not in self.STATUS: return
        status = self.STATUS[msg_status]
        uid = msg["c"]
        eid = msg["i"]
        event = UserEvent(uid=uid, eid=eid, status=status)
        self.emit(event)

    def on_stop(self) -> None:
        pass

    def post_run(self) -> None:
        self.socket_manager.stop()
        self.socket_manager.join()

    def start_candles(self, symbol: str, interval: Interval) -> None:
        self.log(f"Start socket for {symbol} {interval}")
        if interval not in self.INTERVALS or (symbol, interval) in self.open_sockets: return
        self.socket_manager.start_kline_socket(self._candle_handler, symbol, BinanceConnector.INTERVALS[interval])
        self.open_sockets.add((symbol, interval))

    def _candle_handler(self, msg: dict) -> None:
        closed = msg["k"]["x"]
        msg_interval = msg["k"]["i"]
        if not closed or msg_interval not in self.INTERVALS.inverse: return
        symbol = msg["s"]
        interval = self.INTERVALS.inverse[msg_interval]
        time = int(int(msg["k"]["t"])/1000)
        open = float(msg["k"]["o"])
        close = float(msg["k"]["c"])
        high = float(msg["k"]["h"])
        low = float(msg["k"]["l"])
        volume = float(msg["k"]["v"])
        candle = Candle(time=time, open=open, close=close, high=high, low=low, volume=volume)
        event = CandleEvent(name=self.EXCHANGE, symbol=symbol, interval=interval, candle=candle)
        self.emit(event)

    def submit(self, execution_order: Single) -> str:
        params = {"symbol": execution_order.symbol, "newClientOrderId": execution_order.uid,
                  "side": SIDE_BUY if execution_order.command is Command.BUY else SIDE_SELL}

        if execution_order.price > 0:
            params["type"] = ORDER_TYPE_LIMIT
            params["quantity"] = round(execution_order.quote, 6)
            params["price"] = execution_order.price
            params["timeInForce"] = TIME_IN_FORCE_GTC
        else:
            params["type"] = ORDER_TYPE_MARKET
            if execution_order.quote:
                params["quantity"] = execution_order.quote
            elif execution_order.base:
                params["quoteOrderQty"] = execution_order.base

        response = self.client.create_order(**params)
        return str(response["orderId"])

    def cancel(self, execution_order: Single) -> str:
        params = {"symbol": execution_order.symbol, "orderId": int(execution_order.eid), "origClientOrderId": execution_order.uid}
        response = self.client.cancel_order(**params)
        return response["clientOrderId"]
