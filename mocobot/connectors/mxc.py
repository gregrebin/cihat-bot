from mocobot.application.connector import Connector, Recipe, UserEvent, CandleEvent
from mocobot.application.market import Interval, TimeFrame, Candle
from mocobot.application.order import Single, Command, Status
from socketio import Client
from bidict import bidict
from typing import Set, Tuple
import requests
import time
import hmac
import hashlib


class MxcConnector(Connector):

    EXCHANGE = "mxc"

    INTERVALS = bidict({
        Interval(1, TimeFrame.MINUTE): "Min1",
        Interval(5, TimeFrame.MINUTE): "Min5",
        Interval(15, TimeFrame.MINUTE): "Min15",
        Interval(30, TimeFrame.MINUTE): "Min30",
        Interval(1, TimeFrame.HOUR): "Min60",
        Interval(1, TimeFrame.DAY): "Day1",
        Interval(1, TimeFrame.MONTH): "Month1",
    })
    STATUS = {
        1: Status.SUBMITTED,
        2: Status.FILLED,
        3: Status.SUBMITTED,
        4: Status.CANCELLED,
        5: Status.CANCELLED,
    }
    TRADE_TYPES = {
        Command.BUY: "BID",
        Command.SELL: "ASK",
    }
    ORDER_TYPE_LIMIT = "LIMIT_ORDER"
    ORDER_TYPE_MARKET = "MARKET_ORDER"

    def post_init(self) -> None:
        self.open_sockets: Set[Tuple[str, Interval]] = set()
        self.sio = Client(request_timeout=60000, reconnection_delay=500)
        self.sio.on("push.kline", self._kline_handler)
        self.sio.on("push.personal.order", self._order_handler)

    def _kline_handler(self, msg: dict):
        data = msg["data"]
        symbol = data["symbol"]
        interval = self.INTERVALS.inverse[data["interval"]]
        time = data["t"]
        open = data["o"]
        close = data["c"]
        high = data["h"]
        low = data["l"]
        volume = data["v"]
        candle = Candle(time=time, open=open, close=close, high=high, low=low, volume=volume)
        event = CandleEvent(exchange=self.EXCHANGE, symbol=symbol, interval=interval, candle=candle)
        self.emit(event)

    def _order_handler(self, msg: dict):
        data = msg["data"]
        if data["status"] not in self.STATUS: return
        status = self.STATUS[data["status"]]
        eid = data["id"]
        event = UserEvent(eid=eid, status=status, uid="")
        self.emit(event)

    @property
    def exchange(self) -> str:
        return self.EXCHANGE

    def pre_run(self) -> None:
        self.sio.connect('wss://www.mxc.com', transports=['websocket', 'polling'])
        self.sio.emit('sub.personal', self._params_ws())

    async def on_run(self) -> None:
        pass

    def on_stop(self) -> None:
        pass

    def post_run(self) -> None:
        self.sio.disconnect()

    async def start_socket(self, symbol: str, interval: Interval):
        self.log(f"Start socket for {symbol} {interval}")
        if interval not in self.INTERVALS or (symbol, interval) in self.open_sockets: return
        self.sio.emit('sub.kline', {"symbol": symbol, "interval": self.INTERVALS[interval]})
        self.open_sockets.add((symbol, interval))

    def submit(self, order: Single) -> Recipe:
        params = self._params("POST", "/open/api/v2/order/place")
        json = {
            'symbol': order.symbol,
            'price': order.price,
            'trade_type': self.TRADE_TYPES[order.command],
            "client_order_id": order.uid,
            "order_type": self.ORDER_TYPE_LIMIT if order.price > 0 else self.ORDER_TYPE_MARKET,
            "quantity": order.base if order.price <= 0 and order.command is Command.BUY else order.quote
        }
        response = requests.post("https://www.mxc.com/open/api/v2/order/place", params=params, json=json).json()
        if response["code"] == 200:
            return Recipe(eid=response["data"], status=Status.SUBMITTED)
        else:
            return Recipe(eid=order.eid, status=Status.REJECTED)

    def cancel(self, order: Single) -> Recipe:
        original_params = {"order_ids": order.eid, "client_order_ids": order.uid}
        params = self._params("DELETE", "/open/api/v2/order/cancel", original_params=original_params)
        response = requests.delete("https://www.mxc.com/open/api/v2/order/cancel", params=params).json()
        print(response)
        if response["code"] == 200:
            return Recipe(eid=order.eid, status=Status.CANCELLED)
        else:
            return Recipe(eid=order.eid, status=Status.REJECTED)

    def _params(self, method, path, original_params=None):
        params = {'api_key': self.username, 'req_time': int(time.time())}
        if original_params is not None:
            params.update(original_params)
        params_str = '&'.join('{}={}'.format(k, params[k]) for k in sorted(params))
        to_sign = '\n'.join([method, path, params_str])
        params.update({'sign': hmac.new(self.password.encode(), to_sign.encode(), hashlib.sha256).hexdigest()})
        return params

    def _params_ws(self):
        t = int(time.time())
        data = f"api_key={self.username}&req_time={t}&api_secret={self.password}"
        sign = hashlib.md5(data.encode("utf8")).hexdigest()
        return {"api_key": self.username, "sign": sign, "req_time": t}
