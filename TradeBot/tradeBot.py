from TradeBot.binanceAPI import BinanceAPI
import TradeBot.config as config
from Strategy.strategy import Broker
import time
import math
from datetime import datetime


def _getFromListWithDictKey(_list, key, value):
    return next(item for item in _list if item[key] == value)


class TradeBot:
    def __init__(self, strategy, cashName='USDT', coinName='BTC', requestInterval=0.5):
        self.client = BinanceAPI(config.api_key, config.api_secret)
        self.cashName = cashName
        self.coinName = coinName
        self.strategy = strategy
        self.requestInterval = requestInterval  # sec to wait for next price request

    def run(self):
        broker = TradeBroker(self.client, self.cashName, self.coinName)
        self.strategy.broker = broker

        while True:
            broker.price = self.getPrice()
            broker.time = datetime.now()
            self.strategy.next()
            time.sleep(self.requestInterval)

    def getPrice(self):
        orderBook = self.client.get_order_books(market=self.coinName + self.cashName)
        return (float(orderBook["bids"][0][0]) + float(orderBook["asks"][0][0])) / 2

class TradeBroker(Broker):
    def __init__(self, client, cashName, coinName):
        # precision
        info_symbols = client.get_exchange_info()["symbols"]
        info_symbol = _getFromListWithDictKey(info_symbols, "symbol", coinName + cashName)
        info_symbol_filters = info_symbol["filters"]
        info_symbol_LOT_SIZE = _getFromListWithDictKey(info_symbol_filters, "filterType", "LOT_SIZE")
        step_size = float(info_symbol_LOT_SIZE["stepSize"])
        precision = int(round(-math.log(step_size, 10), 0))

        # commission
        accountInfo = client.get_account()
        commission = accountInfo["takerCommission"] / 10000

        super().__init__()
        self.commission = commission
        self.client = client
        self.precision = precision
        self.cashName = cashName
        self.coinName = coinName
        self.getAccount()  # set cash and boughtAmount here

    def buy(self, amount):
        amount = self._floor(amount)
        res = self.client.buy_market(self.coinName+self.cashName, amount)
        print(f"[{datetime.now()}] buy: {res}")
        self.getAccount()

    def sell(self, amount):
        amount = self._floor(amount)
        res = self.client.sell_market(self.coinName+self.cashName, amount)
        print(f"[{datetime.now()}] sell: {res}")
        self.getAccount()

    def close(self):
        self.sell(self.boughtAmount)

    def _floor(self, value):
        p = math.pow(10, self.precision)
        return math.floor(value * p) / p

    def getAccount(self):
        data = self.client.get_account()
        assets = data['balances']
        self.cash = float(_getFromListWithDictKey(assets, "asset", self.cashName)["free"])
        self.boughtAmount = float(_getFromListWithDictKey(assets, "asset", self.coinName)["free"])
        print(f"cash: {self.cash}, bought: {self.boughtAmount}")