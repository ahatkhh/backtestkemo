from Strategy.strategy import Strategy
import pandas as pd
from datetime import datetime

class DCA_Strategy1(Strategy):
    def __init__(self, isRealTime=False):
        super().__init__()
        self.isRealTime = isRealTime

        # parameters
        self.trigPs = [0.60, 0.80, 0.8425, 0.9023, 0.9268]
        self.invests = [i/400 for i in [100, 20, 30, 42, 53, 55]]

        # self.trigPs = [0.60, 0.80, 0.8250, 0.828, 0.8837, 0.9]
        # self.invests = [i/400 for i in [100, 20, 40, 60, 60, 50, 70]]


        self.trail_profit = 0.1
        self.trail_dca = 0.20
        self.profitP = 0.50
        self.stopLossP = 1

        # inner values
        self.initialCash = 0
        self.initialPrice = 0
        self.initialBought = 0

        self.average = 0
        self.intervalNum = 0
        self.intervals = []

        self.trail_lowest = 1000000000000
        self.trail_highest = 0

        self.stopLossPrice = 0

        # for plotting
        self.events = [] # [{"type": "Buy", "time":, "price":, "average":, "total":,}, ...]
        self.boughtTotal = []
        self.averages = []

    def next(self):
        super().next()

        # initial buy
        if self.initialPrice == 0:
            self.initialCash = self.broker.cash
            self.initialPrice = self.broker.price
            self.initialBought = self.initialCash * self.invests[0] / self.broker.price
            self.average = self.broker.price

            self.intervals = [self.broker.price * (1-self.trigPs[0])]
            self.intervalNum = 1

            self.trail_lowest = 1000000000000
            self.trail_highest = 0

            self.stopLossPrice = 0

            self.buy(self.initialBought)
            self._handleEvent({"type": "Start", "time": self.broker.time, "price": self.broker.price, "average": self.average,
                               "total": self.broker.total})
        # dca zone
        elif self.broker.price < self.average:
            if self.broker.price < self.stopLossPrice:
                self.close()
                self.initialPrice = 0
                self._handleEvent(
                    {"type": "Reset", "time": self.broker.time, "price": self.broker.price, "average": self.average,
                     "total": self.broker.total})

            self.trail_lowest = min(self.trail_lowest, self.broker.price)

            max_interval = min(len(self.trigPs), len(self.invests) - 1)
            if self.intervalNum <= max_interval and\
                    self.trail_lowest * (1 + self.trail_dca) < self.broker.price < self.intervals[-1]:
                buyAmount = self.initialCash * self.invests[self.intervalNum] / self.broker.price
                self.buy(buyAmount)
                self.average = (self.initialCash - self.broker.cash) / self.broker.boughtAmount
                if self.intervalNum < max_interval:
                    self.intervals.append(self.average * (1-self.trigPs[self.intervalNum]))
                else:
                    self.stopLossPrice = self.broker.price * (1 - self.stopLossP)
                self.intervalNum += 1
                self.trail_highest = 0
                self._handleEvent({"type": "DCA Buy", "time": self.broker.time, "price": self.broker.price, "average": self.average,
                                   "total": self.broker.total})
        # profit zone
        else:
            self.trail_highest = max(self.trail_highest, self.broker.price)
            if self.average * (1 + self.profitP) < self.broker.price < self.trail_highest * (1 - self.trail_profit):
                self.close()
                self.initialPrice = 0
                self._handleEvent({"type": "Reset", "time": self.broker.time, "price": self.broker.price, "average": self.average,
                                   "total": self.broker.total})

        if not self.isRealTime:
            self.boughtTotal.append(self.broker.boughtTotal)
            self.averages.append(self.average)

    def end(self):
        super().end()
        df = pd.DataFrame(self.events)
        if len(df) == 0:
            return

        df = df.set_index("time")
        # print(df)

        # log df
        f = open("log.txt", "a+")
        f.write("\n")
        f.write(str(datetime.now()) + "\n")
        f.write(self.name + "\n")
        f.write(df.to_string())
        f.write("\n")

        # draw bought total and average
        self.plots.append({"values": self.boughtTotal, "params": {"color": "blue"}, "onCash": True})
        self.plots.append({"values": self.averages, "params": {"color": "orange", "linewidth": 0.5}, "toBack": True})

        # draw DCA buying dates
        df_rev_sell = df.loc[df["type"] == "DCA Buy"]
        self.plots.append({"values": df_rev_sell["price"], "scatter": True,
                           "x": df_rev_sell.index, "params": {"color": "red"}})

        # draw system reset dates
        df_reset = df.loc[df["type"] == "Reset"]

        self.plots.append({"values": df_reset["price"], "scatter": True, "x": df_reset.index,
                           "params": {"color": "green"}})
        self.plots.append({"values": df_reset["total"], "scatter": True, "x": df_reset.index,
                           "params": {"color": "green"}, "onCash": True})
        self.plots.append(
            {"values": [round(n) for n in df_reset["total"]], "text": True, "x": df_reset.index,
             "y": df_reset["total"],
             "params": {"fontsize": 7, "horizontalalignment": "center", "verticalalignment": "bottom"},
             "onCash": True})

    def _handleEvent(self, event):
        if self.isRealTime:
            print(f"{event}")
        else:
            self.events.append(event)



        # self.trigPs = [0.1, 0.1822, 0.2579, 0.3271, 0.4593, 0.5717, 0.6551, 0.6968, 7519, 7596, 7891, 7626, 7913, 7763,
        #                0.8035, 0.7625, 0.7920, 0.8263, 0.8419, 0.8559, 0.8399, 0.8798]
        # self.invests = [i/2000 for i in [100, 25, 25, 30, 31, 60, 50, 50, 50, 74, 55, 85, 70, 90,
        #                                  80, 125, 55, 75, 120, 135, 175, 165, 275]]