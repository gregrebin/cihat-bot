from mocobot.application.connector import Connector, Recipe
from mocobot.application.market import Interval
from mocobot.application.order import Single, Command, Status
import requests
import time
import hmac
import hashlib


class MxcConnector(Connector):

    EXCHANGE = "mxc"

    TRADE_TYPES = {
        Command.BUY: "BID",
        Command.SELL: "ASK",
    }
    ORDER_TYPE_LIMIT = "LIMIT_ORDER"
    ORDER_TYPE_MARKET = "MARKET_ORDER"

    @property
    def exchange(self) -> str:
        return self.EXCHANGE

    def pre_run(self) -> None:
        pass

    async def on_run(self) -> None:
        pass

    def on_stop(self) -> None:
        pass

    def post_run(self) -> None:
        pass

    def start_socket(self, symbol: str, interval: Interval):
        pass

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
