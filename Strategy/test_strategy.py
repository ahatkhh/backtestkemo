from Strategy.strategy import Strategy
import pandas as pd
from datetime import datetime

class Test_Strategy(Strategy):
    def __init__(self, buyRatio=0.07, stop_loss=0.005, make_profit=0.005, min_amount=1e-6):
        super().__init__()
        self.buyRatio = buyRatio
        self.stop_loss = stop_loss
        self.make_profit = make_profit
        self.min_amount = min_amount

        self.buy_price = 0

    def next(self):
        super().next()

        if self.broker.boughtAmount > self.min_amount:
            if self.price > (1 + self.make_profit) * self.buy_price\
                    or self.price < (1 - self.stop_loss) * self.buy_price:
                self.close()
        else:
            self.buy(self.broker.cash * self.buyRatio / self.price)
            self.buy_price = self.price

    def end(self):
        super().end()
